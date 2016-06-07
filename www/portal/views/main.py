import json

from django.views.generic import TemplateView
from django.utils.translation import gettext as _
from django.shortcuts import Http404
from django.shortcuts import get_object_or_404
from django.template import loader
from django.http import HttpResponse
from django.core.cache import cache

from toolware.utils import mixin
from articleware.models import Article
from articleware.utils import get_active_categories
from articleware.utils import is_user_active

from .. import utils as util
from .. import defaults as defs


class IndexView(mixin.CsrfProtectMixin, TemplateView):
    """
    Index View
    """
    article_flavor = "Article"

    def get_template_names(self):
        template_name = util.get_template_path("index/main.html")
        return template_name

    def get_data(self):

        cache_on = not is_user_active(self.request, self.article_flavor)
        if cache_on:
            cache_key = 'articles:index-summary-by-categories'
            data = cache.get(cache_key)
            if data:
                return data

        data = []
        excluded = []
        categories = get_active_categories()
        for category in categories:
            try:
                article = Article.objects \
                    .filter(status=Article.ARTICLE_STATUS_PUBLIC) \
                    .filter(flavor=Article.ARTICLE_FLAVOR_ARTICLE) \
                    .exclude(author__is_active=False) \
                    .exclude(id__in=excluded) \
                    .filter(categories__slug=category.slug) \
                    .latest('published_at')
            except Article.DoesNotExist:
                pass
            else:
                if article:
                    excluded.append(article.id)
                    data.append({
                        'category': category,
                        'article': article
                    })

        if cache_on:
            cache.set(cache_key, data, defs.PORTAL_ARTICLE_SEARCH_CACHE_TIMEOUT_MINUTES)

        return data

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        data = self.get_data()
        context.update({'category_summary': data})
        return context
