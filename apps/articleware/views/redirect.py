
from django.views.generic import TemplateView
from django.shortcuts import Http404
from django.shortcuts import get_object_or_404
from django.http import HttpResponsePermanentRedirect

from ..models import Article
from .. import utils as util


class ArticleShortUrlView(TemplateView):
    """
    Article Short URL View
    """
    template_name = '404.html'

    def get_object(self, queryset=None):
        uuid = self.kwargs['uuid']
        obj = get_object_or_404(Article, uuid=uuid)
        return obj

    def get(self, *args, **kwargs):
        obj = self.get_object()
        return HttpResponsePermanentRedirect(obj.get_absolute_url())


class ArticleSecurifyUrlView(TemplateView):
    """
    Securify URL View. Redirect all http external url.
    Example: allow http urls on https sites.
    """
    template_name = '404.html'

    def get(self, *args, **kwargs):
        url = self.request.GET.get('url', '').strip()
        if not url:
            raise Http404
        sig = self.request.GET.get('sig', '')
        if not sig:
            raise Http404
        if sig != util.get_url_salted_hash(url):
            raise Http404
        return HttpResponsePermanentRedirect(url)
