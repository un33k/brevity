from django.conf.urls import patterns, url, include

from .views import *


profiles_urls = patterns('',
    url(
        r'^create$',
        ProfileCreateAPIView.as_view(),
        name='api-profile-create',
    ),
    url(
        r'^list$',
        ProfileListAPIView.as_view(),
        name='api-profile-list',
    ),
    url(
        r'^(?P<pk>[0-9]+)/update$',
        ProfileUpdateAPIView.as_view(),
        name='api-profile-update',
    ),
    url(
        r'^retrieve$',
        ProfileRetrieveAPIView.as_view(),
        name='api-profile-retrieve',
    ),
    url(
        r'^(?P<pk>[0-9]+)/retrieve$',
        ProfileRetrieveAPIView.as_view(),
        name='api-profile-retrieve',
    ),
    url(
        r'^(?P<pk>[0-9]+)/delete$',
        ProfileDeleteAPIView.as_view(),
        name='api-profile-delete',
    ),
    url(
        r'^password/change$',
        ProfilePasswordChangeAPIView.as_view(),
        name='api-profile-password-change',
    ),
    url(
        r'^(?P<pk>[0-9]+)/password/clear$',
        ProfilePasswordClearAPIView.as_view(),
        name='api-profile-password-clear',
    ),
)
