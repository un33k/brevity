import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic import DeleteView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.template import RequestContext
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Q

from toolware.utils.mixin import LoginRequiredMixin
from toolware.utils.mixin import CsrfProtectMixin
from toolware.utils.mixin import DeleteMixin

from ..models import Article
from ..models import Image
from ..models import Snippet

from ..forms import ArticleForm

from .. import utils as util
from .. import defaults as defs
from . common import *


class ArticleAddView(LoginRequiredMixin, CsrfProtectMixin, CreateView, ArticleHelperMixin):
    """
    Creates new article for this user (author)
    """
    model = Article
    form_class = ArticleForm
    article_flavor = "Article"

    def get_template_names(self):
        template_name = util.get_template_path("main.html")
        return template_name

    def get_success_url(self):
        return reverse('articleware:article_update', kwargs={'pk': self.object.id})

    def get_form_kwargs(self):
        kwargs = super(ArticleAddView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.object.author or self.request.user
        self.object.editor = self.object.editor or self.object.author
        self.object.save()
        form.save_m2m()
        return super(ArticleAddView, self).form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, CsrfProtectMixin, UpdateView, ArticleHelperMixin):
    """
    Creates new article for this user (author)
    """
    form_class = ArticleForm
    article_flavor = "Article"

    def get_template_names(self):
        template_name = util.get_template_path("main.html")
        return template_name

    def get_ajax_template_name(self):
        template_name = util.get_template_path("form_update.html")
        return template_name

    def get_form_kwargs(self):
        kwargs = super(ArticleUpdateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        kwargs.update({'instance': self.object})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ArticleUpdateView, self).get_context_data(**kwargs)
        self.prepare_snippets_for_article(self.object)
        context['article'] = self.object
        return context

    def response_ajax(self, form, article, status):
        quiet = self.kwargs.get('quiet', False)
        if quiet:
            return HttpResponse(json.dumps({'status': status}), content_type="application/json")

        if status == 200:
            form = self.form_class(instance=self.object, request=self.request)
        msg = 'Article saved.'.format(self.article_flavor)
        t = loader.get_template(self.get_ajax_template_name())
        c = RequestContext(self.request, {'form': form, 'article': article})
        resp = {
            'status': status,
            'message': '{} saved.'.format(self.article_flavor) if status == 200 else '{} not saved'.format(self.article_flavor),
            'html': t.render(c)
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.object.author or self.request.user
        self.object.editor = self.object.editor or self.object.author
        self.object.save()
        form.save_m2m()
        if self.request.is_ajax():
            return self.response_ajax(form, self.object, 200)
        return super(ArticleUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return self.response_ajax(form, self.object, 400)
        return super(ArticleUpdateView, self).form_invalid(form)

    def get_object(self, queryset=None):
        self.created = False
        pk = self.kwargs.get('pk', None)
        obj = get_object_or_404(Article, author=self.request.user, pk=pk)
        return obj

    def dispatch(self, *args, **kwargs):
        util.set_user_activity_state(self.request, self.article_flavor)
        return super(ArticleUpdateView, self).dispatch(*args, **kwargs)


class ArticleFeaturedToggleView(LoginRequiredMixin, CsrfProtectMixin, TemplateView):
    """
    Toggle the featured option of an article.
    """
    article_flavor = "Article"

    def set_featured(self):
        pk = self.kwargs.get('pk', None)
        obj = get_object_or_404(Article, pk=pk)
        obj.featured = not obj.featured
        obj.save()
        data = {
            'featured': 'YES' if obj.featured else 'NO'
        }
        return HttpResponse(json.dumps(data), content_type="application/json")

    def post(self, *args, **kwargs):
        util.set_user_activity_state(self.request, self.article_flavor)
        return self.set_featured()


class ArticlePublicListView(LoginRequiredMixin, TemplateView):
    """
    Article Public List View.
    """
    def get_template_names(self):
        template_name = util.get_template_path("list.html")
        return template_name

    def get_article_status(self):
        return Article.ARTICLE_STATUS_PUBLIC

    def get_articles(self):
        articles = Article.objects \
            .filter(author=self.request.user) \
            .filter(flavor=Article.ARTICLE_FLAVOR_ARTICLE) \
            .filter(status=self.get_article_status()) \
            .exclude(Q(headline__isnull=True) | Q(headline__exact='')) \
            .order_by('-updated_at', '-created_at')
        return articles

    def get_context_data(self, **kwargs):
        context = super(ArticlePublicListView, self).get_context_data(**kwargs)
        context['articles'] = self.get_articles()
        context['article_type'] = self.get_article_status()
        return context


class ArticleArchivedListView(ArticlePublicListView):
    """
    Article Archived List View.
    """
    def get_article_status(self):
        status = Article.ARTICLE_STATUS_ARCHIVED
        return status


class ArticleUnlistedListView(ArticlePublicListView):
    """
    Article Unlisted List View.
    """
    def get_article_status(self):
        status = Article.ARTICLE_STATUS_UNLISTED
        return status


class ArticlePrivateListView(ArticlePublicListView):
    """
    Article Private List View.
    """
    def get_article_status(self):
        status = Article.ARTICLE_STATUS_PRIVATE
        return status
