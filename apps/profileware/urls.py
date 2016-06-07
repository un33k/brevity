from django.conf import settings
from django.conf.urls import url
from django.conf.urls import patterns

from .views import *
from . import defaults as defs


urlpatterns = [
    url(
        r'^profile$',
        UserProfileUpdateView.as_view(),
        name='account_profile',
    ),
    url(
        r'^profile/settings$',
        AccountPreferencesView.as_view(),
        name='account_profile_preferences'
    ),
    url(
        r'^settings/social$',
        AccountSocialAssociationView.as_view(),
        name='account_settings_social'
    ),
    url(
        r'',
        AccountIndexView.as_view(),
        name='account_index'
    ),
]
