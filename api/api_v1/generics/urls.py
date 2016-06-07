from django.conf.urls import patterns, url, include

from .views import *


generics_urls = patterns('',
    url(
        r'^csrf/retrieve$',
        GenericsCsrfAPIView.as_view(),
        name='api-generics-csrf-retrieve',
    ),
)
