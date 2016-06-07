from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib.flatpages.sitemaps import FlatPageSitemap as DjangoFlatPageSitemap

from articleware.models import Article
from articleware.utils import get_approved_writer_group_name

SITE_PROTOCOL = getattr(settings, 'SITE_PROTOCOL', 'http')


class ArticleSitemap(Sitemap):
    """
    Sitemap for Articles
    """
    changefreq = "never"
    priority = 0.5
    limit = 10000
    protocol = SITE_PROTOCOL

    def items(self):
        approved_group = get_approved_writer_group_name()
        queryset = Article.objects \
            .filter(status=Article.ARTICLE_STATUS_PUBLIC) \
            .filter(flavor=Article.ARTICLE_FLAVOR_ARTICLE) \
            .filter(author__is_active=True) \
            .filter(author__groups__name=approved_group) \
            .order_by('-published_at')
        return queryset

    def lastmod(self, obj):
        return obj.published_at

    def location(self, obj):
        return obj.get_absolute_url()


class BlogSitemap(Sitemap):
    """
    Sitemap for Blog
    """
    changefreq = "never"
    priority = 0.5
    limit = 10000
    protocol = SITE_PROTOCOL

    def items(self):
        queryset = Article.objects \
            .filter(status=Article.ARTICLE_STATUS_PUBLIC) \
            .filter(flavor=Article.ARTICLE_FLAVOR_BLOG) \
            .order_by('-published_at')
        return queryset


class StaticViewSitemap(Sitemap):
    """
    Sitemap for static pages
    """
    changefreq = 'daily'
    priority = 1.0
    protocol = SITE_PROTOCOL

    def items(self):
        return ['portal:index_view', ]

    def location(self, item):
        return reverse(item)


class FlatPageSitemap(DjangoFlatPageSitemap):
    changefreq = "never"
    priority = 0.5
    limit = 10000
    protocol = SITE_PROTOCOL
