from django.conf.urls import patterns, url, include

from .profiles.urls import profiles_urls
from .generics.urls import generics_urls
from . import views

urlpatterns = patterns('',
    url(r'^profile/', include(profiles_urls)),
    url(r'^generics/', include(generics_urls)),
    url(r'', views.api_root),
)
