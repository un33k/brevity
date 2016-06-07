
from django.core.cache import cache
from django.db.models import Q

from articleware.models import Article
from articleware.utils import is_user_active

from .search import ArticleSearchView
from .. import defaults as defs


class ArticleBlogView(ArticleSearchView):
    """
    Article Blog View
    """
    url_path = 'blog'
    article_flavor = 'Blog'

    def get_data(self):
        data = super(ArticleBlogView, self).get_data()
        data['referrer'] = 'blog'
        return data

    def get_articles_by_search_params(self):
        """
        Returns list of related article based on blog, categories, targets, tags and author.
        """
        cache_on = not is_user_active(self.request, self.article_flavor)
        if cache_on:
            cache_key = self.get_cache_key_for_params_by_type('articles:blog')
            articles = cache.get(cache_key)
            if articles:
                return articles

        text_query = self.get_text_query_list()
        queryset = Article.objects \
            .filter(status=Article.ARTICLE_STATUS_PUBLIC) \
            .filter(flavor=Article.ARTICLE_FLAVOR_BLOG) \
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

        articles = queryset.distinct().order_by('-published_at')

        if cache_on:
            cache.set(cache_key, articles, defs.PORTAL_ARTICLE_SEARCH_CACHE_TIMEOUT_MINUTES)

        return articles
