from django.conf import settings
from django.contrib import admin
from django.shortcuts import render
from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.sitemaps import views as sitemap_views
from django.views.decorators.cache import cache_page
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

from portal import views as pviews
from views import PlainTextView

sitemaps = {
    'site': pviews.StaticViewSitemap,
    'articles': pviews.ArticleSitemap,
    'blogs': pviews.BlogSitemap,
    'pages': pviews.FlatPageSitemap,
}

ADMIN_URI = getattr(settings, 'SITE_ADMIN_URL_PATH', 'admin')
admin.site.site_header = '{} Admin'.format(settings.SITE_NAME)

try:
    favicon = staticfiles_storage.url('img/favicons/favicon.ico')
except ValueError:  # unable to connect to cdn @ this time
    favicon = None

try:
    logo = staticfiles_storage.url('img/logos/logo.png')
except ValueError:  # unable to connect to cdn @ this time
    logo = None

urlpatterns = [
    url(r'^{}/'.format(ADMIN_URI.rstrip('/')), include(admin.site.urls)),
]

# Apps
urlpatterns += [
    url(r'^contact/', include('contactware.urls', namespace='contactware')),

    url(r'^account/user/', include('userware.urls')),
    url(r'^account/user/', include('userware.urls', namespace='userware')),
    url(r'^account/user/', include('profileware.urls', namespace='profileware')),

    url(r'^account/ads/', include('adware.urls', namespace='adware')),

    url(r'^article/', include('articleware.urls', namespace='articleware')),
    url(r'^account/article/', include('articleware.urls', namespace='articleware')),
    url(r'^trac/', include('tracware.urls', namespace='tracware')),
]

urlpatterns += [
    url(r'^sitemap.xml$',
        cache_page(3600)(sitemap_views.index),
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'},
    ),

    url(r'^sitemap-(?P<section>.+)\.xml$',
        cache_page(3600)(sitemap_views.sitemap),
        {'sitemaps': sitemaps},
        name='sitemaps'
    ),
]

# Plain Text Views
urlpatterns += [
    url(r'^robots\.txt$', PlainTextView.as_view(template_name='robots.txt')),
    url(r'^crossdomain\.xml$', PlainTextView.as_view(template_name='crossdomain.xml')),
]

if favicon:
    urlpatterns += [
        url(r'^favicon\.ico$', RedirectView.as_view(url=favicon))
    ]
if logo:
    urlpatterns += [
        url(r'^logo\.png$', RedirectView.as_view(url=logo))
    ]

urlpatterns += [
    url(r'^autocomplete/', include('autocomplete_light.urls')),
]

# Rest API Views
if 'rest_framework' in settings.INSTALLED_APPS:
    if 'api_v1' in settings.INSTALLED_APPS:
        urlpatterns += [
            url(r'^api/v1/', include('api_v1.urls', namespace='api_v1')),
        ]

    if 'rest_framework_swagger' in settings.INSTALLED_APPS:
        urlpatterns += [
            url(r'^swagger/', include('rest_framework_swagger.urls', namespace='swagger')),
        ]

    urlpatterns += [
        url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
        url(r'^api/auth/token/', 'rest_framework.authtoken.views.obtain_auth_token'),
    ]

# Debug static / media
if settings.DEBUG:
    urlpatterns += [
        url(r'^m/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^s/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
    ]

# Social Login
urlpatterns += [
    url('', include('social.apps.django_app.urls', namespace='social')),
]

# Everything else
urlpatterns += [
    url(r'', include('portal.urls', namespace='portal')),
]


@requires_csrf_token
def handler500(request):
    return render(request, '500.html')
