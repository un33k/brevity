
import json

from django.views.generic import TemplateView
from django.utils.translation import gettext as _
from django.shortcuts import Http404
from django.shortcuts import get_object_or_404
from django.http import HttpResponsePermanentRedirect
from django.contrib import messages
from django.template import RequestContext
from django.template import loader
from django.http import HttpResponse
from django.core.cache import cache

from toolware.utils import mixin
from articleware.models import Article
from articleware.utils import is_user_active

from .. import utils as util
from .. import defaults as defs


class ArticleView(mixin.CsrfProtectMixin, TemplateView):
    """
    Article Object View
    """
    article_flavor = "Article"

    def get_template_names(self):
        template_name = util.get_template_path("article/entry/main.html")
        return template_name

    def get_object(self, queryset=None):
        uuid = self.kwargs['uuid']
        cache_on = not is_user_active(self.request, self.article_flavor)
        if cache_on:
            cache_key = 'article_individual_{}'.format(uuid)
            article = cache.get(cache_key)
            if article:
                return article

        article = get_object_or_404(Article, uuid=uuid)
        if cache_on:
            cache.set(cache_key, article, defs.PORTAL_ARTICLE_SEARCH_CACHE_TIMEOUT_MINUTES)
        return article

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(ArticleView, self).get_context_data(**kwargs)
        context['referrer'] = 'latest'
        article = self.get_object()
        context['query_string'] = ''
        if article.is_author(user) or article.is_editor(user):
            article.preview = True
            if article.is_public:
                if article.has_approved_author:
                    msg = _('Your article is public and is viewable to everyone.')
                else:
                    msg = _('Your article is public yet not visible. Get your account approved.')
                messages.add_message(self.request, messages.WARNING, msg)
            elif article.is_unlisted:
                msg = _('Your article is unlisted and can only be viewed by URL.')
                messages.add_message(self.request, messages.WARNING, msg)
            else:
                msg = _('Your article is private and is not viewable by anyone else.')
                messages.add_message(self.request, messages.ERROR, msg)
            context['article'] = article
            return context
        elif article.is_public or article.is_unlisted:
            context['article'] = article
            if article.is_unlisted:
                msg = _('This is an unlisted article, think twice before sharing it with others.')
                messages.add_message(self.request, messages.WARNING, msg)
            return context
        raise Http404

    def get(self, *args, **kwargs):
        obj = self.get_object()
        if self.request.user_agent.is_bot:
            if not obj.is_public:
                raise Http404
        slug = self.kwargs['slug']
        if obj.slug != slug:
            return HttpResponsePermanentRedirect(obj.get_absolute_url())
        return super(ArticleView, self).get(*args, **kwargs)


class ArticlePageView(ArticleView):
    def get_template_names(self):
        template_name = util.get_template_path("article/entry/main.html")
        return template_name

    def get_object(self, queryset=None):
        slug = self.kwargs['slug']
        obj = get_object_or_404(Article, slug=slug)
        return obj

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(ArticleView, self).get_context_data(**kwargs)
        article = self.get_object()
        context['query_string'] = ''
        context['article'] = article
        return context


class ArticleShareView(mixin.CsrfProtectMixin, TemplateView):
    """
    Share View
    """
    def get_template_names(self):
        template_name = util.get_template_path("article/misc/share.html")
        return template_name

    def get_context_data(self, **kwargs):
        context = super(ArticleShareView, self).get_context_data(**kwargs)
        self.data = {
            'article': self.get_object()
        }
        context.update(self.data)
        return context

    def get_object(self, queryset=None):
        uuid = self.kwargs['uuid']
        article = get_object_or_404(Article, uuid=uuid)
        return article
