from django.conf import settings
from django.conf.urls import url
from django.conf.urls import patterns

from .views import *
from . import defaults as defs

urlpatterns = [

    url(
        r'^add$',
        ArticleAddView.as_view(),
        name='article_add',
    ),
    url(
        r'^update/(?P<pk>[0-9]+)$',
        ArticleUpdateView.as_view(),
        name='article_update',
    ),
    url(
        r'^update/(?P<pk>[0-9]+)/(?P<quiet>[-\w]+)$',
        ArticleUpdateView.as_view(),
        name='article_update'
    ),
    url(
        r'^update/(?P<pk>[0-9]+)/featured/$',
        ArticleFeaturedToggleView.as_view(),
        name='article_featured'
    ),
    url(
        r'list/public$',
        ArticlePublicListView.as_view(),
        name='article_public_list_view',
    ),
    url(
        r'list/unlisted$',
        ArticleUnlistedListView.as_view(),
        name='article_unlisted_list_view',
    ),
    url(
        r'list/private$',
        ArticlePrivateListView.as_view(),
        name='article_private_list_view',
    ),
    url(
        r'list/archived$',
        ArticleArchivedListView.as_view(),
        name='article_archived_list_view',
    ),
    url(
        r'^(?P<uuid>[-\w]+)$',
        ArticleShortUrlView.as_view(),
        name='article_short_url_view'
    ),
    url(
        r'^secure/$',
        ArticleSecurifyUrlView.as_view(),
        name='article_securify_url_view'
    ),

] + [

    url(
        r'^add/blog$',
        ArticleBlogAddView.as_view(),
        name='article_blog_add',
    ),
    url(
        r'^update/blog/(?P<pk>[0-9]+)$',
        ArticleBlogUpdateView.as_view(),
        name='article_blog_update',
    ),
    url(
        r'list/blog$',
        ArticleBlogListView.as_view(),
        name='article_blog_list_view',
    ),

] + [

    url(
        r'^add/page$',
        ArticlePageAddView.as_view(),
        name='article_page_add',
    ),
    url(
        r'^update/page/(?P<pk>[0-9]+)$',
        ArticlePageUpdateView.as_view(),
        name='article_page_update',
    ),
    url(
        r'list/page$',
        ArticlePageListView.as_view(),
        name='article_page_list_view',
    ),

] + [

    url(
        r'^snippet/add/(?P<type>[A-Z]+)/(?P<article>[0-9]+)$',
        SnippetAddView.as_view(),
        name='snippet_add',
    ),
    url(
        r'^snippet/insert/(?P<type>[A-Z]+)/(?P<article>[0-9]+)/(?P<priority>[0-9]+)$',
        SnippetInsertView.as_view(),
        name='snippet_insert',
    ),
    url(
        r'^snippet/update/(?P<pk>[0-9]+)$',
        SnippetUpdateView.as_view(),
        name='snippet_update'
    ),
    url(
        r'^snippet/update/(?P<pk>[0-9]+)/(?P<quiet>[-\w]+)$',
        SnippetUpdateView.as_view(),
        name='snippet_update'
    ),
    url(
        r'^snippet/swap/priority/(?P<direction>[A-Z]+)/(?P<pk>[0-9]+)$',
        SnippetSwapPriorityView.as_view(),
        name='snippet_swap_priority',
    ),
    url(
        r'^snippet/delete/(?P<pk>[0-9]+)$',
        SnippetDeleteView.as_view(),
        name='snippet_delete',
    ),

] + [

    url(
        r'^image/add$',
        ImageAddView.as_view(),
        name='snippet_image_add',
    ),
    url(
        r'^image/delete/(?P<pk>[0-9]+)$',
        ImageDeleteView.as_view(),
        name='snippet_image_delete',
    ),
    url(
        r'^image/swap/priority/(?P<direction>[A-Z]+)/(?P<pk>[0-9]+)$',
        ImageSwapPriorityView.as_view(),
        name='snippet_image_swap_priority',
    ),

] + [

    url(
        r'^video/add$',
        VideoAddView.as_view(),
        name='snippet_video_add',
    ),
    url(
        r'^video/delete/(?P<pk>[0-9]+)$',
        VideoDeleteView.as_view(),
        name='snippet_video_delete',
    ),
    url(
        r'^video/swap/priority/(?P<direction>[A-Z]+)/(?P<pk>[0-9]+)$',
        VideoSwapPriorityView.as_view(),
        name='snippet_video_swap_priority',
    ),

]
