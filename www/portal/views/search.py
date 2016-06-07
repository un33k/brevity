import json

from django.db.models import Q
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.cache import cache
from django.template import RequestContext
from django.template import loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from toolware.utils import mixin
from toolware.utils.query import get_text_query
from toolware.utils.generic import get_hashed
from articleware.models import Article
from articleware.utils import is_user_active
from articleware.utils import get_approved_writer_group_name
from siteware.utils import profileit

from .. import utils as util
from .. import defaults as defs
from ..templatetags.search import pagination_url

User = get_user_model()


class ArticleSearchViewMixin(mixin.CsrfProtectMixin, TemplateView):
    """
    Article Search View Mixin
    """
    url_path = 'search'
    article_flavor = "Article"

    def get_template_names(self):
        template_name = util.get_template_path("article/search/main.html")
        return template_name

    def get_paginate(self, articles, page=1):
        paginate = Paginator(articles, defs.PORTAL_PAGINATION_NUMBER_PER_PAGE)
        try:
            articles_result = paginate.page(page)
        except PageNotAnInteger:  # first page if not an integer
            articles_result = paginate.page(1)
        except EmptyPage:  # last page for out of range
            articles_result = paginate.page(paginate.num_pages)
        return articles_result

    def get_articles_by_search_params(self):
        """
        Returns list of related article based on categories, targets, tags and author.
        """
        cache_on = not is_user_active(self.request, self.article_flavor)
        if cache_on:
            cache_key = self.get_cache_key_for_params_by_type('articles:latest')
            articles = cache.get(cache_key)
            if articles:
                return articles

        text_query = self.get_text_query_list()
        queryset = Article.objects \
            .filter(status=Article.ARTICLE_STATUS_PUBLIC) \
            .filter(flavor=Article.ARTICLE_FLAVOR_ARTICLE) \
            .exclude(author__is_active=False) \
            .filter(text_query)

        for category in self.selected_categories:
            if category:
                queryset = queryset.filter(categories__slug=category)
        for target in self.selected_targets:
            if target:
                queryset = queryset.filter(targets__slug=target)
        for tag in self.selected_tags:
            if tag:
                queryset = queryset.filter(tags__slug=tag)

        if self.selected_author:
            author = self.selected_author[0]
            queryset = queryset.filter(author__username=author)

        approved_group = get_approved_writer_group_name()
        approved_query = Q(author__groups__name=approved_group)
        if self.request.user.is_authenticated():
            approved_query |= Q(author=self.request.user)
        queryset = queryset.filter(approved_query)

        articles = queryset.distinct().order_by('-published_at')

        if cache_on:
            cache.set(cache_key, articles, defs.PORTAL_ARTICLE_SEARCH_CACHE_TIMEOUT_MINUTES)

        return articles

    def get_text_query_list(self):
        """
        Returns query list for the `text` search fields.
        """
        query = Q()
        if self.selected_query_string:
            search_fields = [
                'headline',
                'author__username',
                'author__last_name',
                'author__first_name',
                'snippet__content',
            ]
            query = get_text_query(self.selected_query_string, search_fields)
        return query

    def redirect_on_multiple_author_query(self):
        authors = self.request.GET.getlist('author')
        query_dict = self.request.GET.copy()
        author_list = []
        valid_authors = User.objects.filter(is_active=True).filter(username__in=authors).distinct()
        if valid_authors:
            author_list.append(valid_authors[0].username)
        else:
            author_list.append(authors[0])
        authors = query_dict.setlist('author', author_list)
        url = util.get_filter_absolute_url(query_dict, self.url_path)
        return HttpResponseRedirect(url)

    def get_valid_query_string(self, query_string_list):
        """
        Returns the last `query` param from `GET` params or return empty string.
        """
        if query_string_list:
            query_string = query_string_list[-1]
        else:
            query_string = ''
        return query_string

    def get_valid_page_number(self, pages):
        """
        Returns page number param from the `GET` params or return 1.
        """
        if pages:
            page = pages[-1]
        else:
            page = 1
        return page

    def get_cache_key_from_params(self, prefix):
        """
        Guarantees consistency in cache key construction.
        """
        params_list = []
        for key, value in self.request.GET.lists():
            if key.lower() == 'page':
                continue
            key_string = '{}-{}'.format(key, '-'.join(value))
            params_list.append(key_string)
        hashed_key = get_hashed(''.join(sorted(params_list)))
        cache_key = '{}-{}'.format(prefix.replace(' ', ''), hashed_key)
        return cache_key

    def get_cache_key_for_params_by_type(self, type):
        """
        Given a type, it returns a unique cache_key based on the type and the request params.
        """
        cache_key = self.get_cache_key_from_params(type)
        return cache_key

    def get_params(self, *args, **kwargs):
        self.selected_query_string = self.get_valid_query_string(self.request.GET.getlist('query'))
        self.selected_categories = self.request.GET.getlist('category')
        self.selected_targets = self.request.GET.getlist('target')
        self.selected_tags = self.request.GET.getlist('tag')
        self.selected_author = self.request.GET.getlist('author')
        self.selected_page = self.get_valid_page_number(self.request.GET.getlist('page'))

    def get_data(self):
        """
        Extracts and returns related params from `GET`.
        """
        articles = self.get_articles_by_search_params()
        paginated_articles = self.get_paginate(articles, self.selected_page)
        filtered_author_username = self.selected_author[0] if self.selected_author else ''
        query_string = self.selected_query_string
        has_next_page = paginated_articles.has_next()
        if has_next_page:
            next_page_number = paginated_articles.next_page_number()
        else:
            next_page_number = ''
        data = {
            'filtered_articles': paginated_articles,
            'has_next_page': has_next_page,
            'curr_page_number': paginated_articles.number,
            'next_page_number': next_page_number,
            'filtered_author_username': filtered_author_username,
            'query_string': query_string,
            'referrer': 'search',
        }
        return data

    def get_context_data(self, **kwargs):
        context = super(ArticleSearchViewMixin, self).get_context_data(**kwargs)
        self.data = self.get_data()
        context.update(self.data)
        return context


class ArticleSearchView(ArticleSearchViewMixin):
    """
    Article Search View
    """
    def handle_ajax(self, **kwargs):
        paginate_template_name = util.get_template_path("article/search/articles.html")
        paginate_template = loader.get_template(paginate_template_name)

        self.data = self.get_data()
        paginate_ctx = RequestContext(self.request, self.data)
        paginate_rendered_data = paginate_template.render(paginate_ctx)

        next_url = ''
        curr_url = ''
        if (self.data['next_page_number']):
            context = self.get_context_data(**kwargs)
            context['request'] = self.request
            curr_url = pagination_url(context, self.data['curr_page_number'])
            next_url = pagination_url(context, self.data['next_page_number'])

        json_data = {
            'html': paginate_rendered_data,
            'curr_url': curr_url,
            'next_url': next_url,
        }
        return HttpResponse(json.dumps(json_data), content_type="application/json")

    def get(self, *args, **kwargs):
        if len(self.request.GET.getlist('author')) > 1:
            return self.redirect_on_multiple_author_query()

        self.get_params()
        if self.request.is_ajax():
            return self.handle_ajax(**kwargs)
        return super(ArticleSearchView, self).get(*args, **kwargs)
