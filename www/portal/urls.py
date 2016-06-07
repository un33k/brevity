from django.conf import settings
from django.conf.urls import url
from django.conf.urls import patterns

from .views import *

from . import defaults as defs

urlpatterns = [
    url(
        r'^article/share/(?P<uuid>[-\w]+)$',
        ArticleShareView.as_view(),
        name='article_share_view'
    ),
    url(
        r'^article/(?P<uuid>[-\w]+)/(?P<slug>[-\w]+)$',
        ArticleView.as_view(),
        name='article_view'
    ),
    url(
        r'^site/(?P<slug>[-\w]+)$',
        ArticlePageView.as_view(),
        name='article_page_view'
    ),
    url(
        r'^search$',
        ArticleSearchView.as_view(),
        name='article_search_view'
    ),
    url(
        r'^latest$',
        ArticleLatestView.as_view(),
        name='article_latest_view'
    ),
    url(
        r'^popular$',
        ArticlePopularView.as_view(),
        name='article_popular_view'
    ),
    url(
        r'^featured$',
        ArticleFeaturedView.as_view(),
        name='article_featured_view'
    ),
    url(
        r'^blog$',
        ArticleBlogView.as_view(),
        name='article_blog_view'
    ),
    url(
        r'^approval/request$',
        ApprovalFormView.as_view(),
        name='approval_confirmation_view'
    ),
    url(
        r'^approval/request/sent$',
        ContactMessageSentView.as_view(),
        name='approval_confirmation_sent_view'
    ),
    url(
        r'^$',
        IndexView.as_view(),
        name='index_view'
    ),
]
