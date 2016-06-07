import json
import random

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic import DeleteView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.template import RequestContext
from django.db import transaction
from django.db import IntegrityError

from toolware.utils.mixin import LoginRequiredMixin
from toolware.utils.mixin import CsrfProtectMixin
from toolware.utils.mixin import DeleteMixin

from ..models import Article
from ..models import Snippet
from ..forms import SnippetTextForm
from ..forms import SnippetImageForm
from ..forms import SnippetVideoForm
from ..forms import SnippetMapForm

from .. import utils as util
from .. import defaults as defs
from .common import *


class SnippetAddView(LoginRequiredMixin, CsrfProtectMixin, TemplateView, ArticleHelperMixin):
    """
    Add an snippet.
    """
    template_name = '404.html'

    def get_or_create(self, article, count, type):
        priority = count + 1

        created = False
        try:
            obj = Snippet.objects.get(article=article, type=type, priority=priority)
        except Snippet.DoesNotExist:
            try:
                with transaction.atomic():
                    obj = Snippet.objects.create(article=article, type=type, priority=priority)
                    created = True
            except IntegrityError:
                obj = Snippet.objects.get(article=article, type=type, priority=priority)

        self.status_code = 200
        self.msg = "Unused {} snippet exists.".format(obj.type)
        if created:
            obj.save()
            self.status_code = 201
            self.msg = '{} snippet created.'.format(obj.type)
        return obj

    def post(self, request, *args, **kwargs):
        article = get_object_or_404(Article, id=self.kwargs.get('article', None))
        count = Snippet.objects.filter(article=article).count()
        type = self.kwargs.get('type', None)
        if type is None:
            resp = {
                'status': 400,
                'message': 'Snippet cannot be created without a type.',
            }
        elif count < defs.ARTICLEWARE_MAX_SNIPPETS_PER_ARTICLE:
            self.object = self.get_or_create(article, count, type)
            self.prepare_snippets_for_article(self.object.article)
            t = loader.get_template(util.get_template_path("snippet/list.html"))
            c = RequestContext(self.request, {'article': self.object.article})
            resp = {
                'snippet_id': self.object.id,
                'status': self.status_code,
                'message': self.msg,
                'html': t.render(c),
            }
        else:
            resp = {
                'status': 400,
                'message': 'Max number of snippets per article is {}.'.format(
                    defs.ARTICLEWARE_MAX_SNIPPETS_PER_ARTICLE),
            }
        return HttpResponse(json.dumps(resp), content_type="application/json")


class SnippetInsertView(SnippetAddView):
    """
    Insert an snippet before the snippet whose priority is passed in.
    """
    def reorder_snippets_for_article(self, article):
        insert_before_this_priority = self.kwargs.get('priority', None)
        if insert_before_this_priority:
            snippets = article.snippets \
                .filter(priority__gte=insert_before_this_priority) \
                .order_by('-priority')
            if snippets:
                last_created = None
                for snippet in snippets:
                    snippet.priority += 1
                    snippet.save()
                    if not last_created:
                        last_created = snippet
                if last_created:
                    last_created.priority = insert_before_this_priority
                    last_created.save()
        return super(SnippetInsertView, self).reorder_snippets_for_article(article)


class SnippetUpdateView(LoginRequiredMixin, CsrfProtectMixin, UpdateView):
    """
    Add an snippet.
    """
    template_name = util.get_template_path("snippet/form.html")

    def get_form_class(self):
        obj = self.get_object()
        if obj.type == obj.SNIPPET_TYPE_TEXT:
            return SnippetTextForm
        if obj.type == obj.SNIPPET_TYPE_IMAGE:
            return SnippetImageForm
        if obj.type == obj.SNIPPET_TYPE_VIDEO:
            return SnippetVideoForm
        if obj.type == obj.SNIPPET_TYPE_MAP:
            return SnippetMapForm

    def get_success_url(self):
        obj = self.get_object(self)
        success_url = reverse('articleware:article_update', kwargs={'pk': obj.article.id})
        return success_url

    def get_object(self, queryset=None):
        obj = get_object_or_404(Snippet, id=self.kwargs.get('pk', None))
        return obj

    def response_ajax(self, form, snippet, status):
        quiet = self.kwargs.get('quiet', False)
        if quiet:
            return HttpResponse(json.dumps({'status': status}), content_type="application/json")

        warning = 1
        if status == 200:
            msg = 'Snippet saved.'
            if form.sanitization_required:
                msg = 'Snippet saved. Tags removed.'
            else:
                warning = 0
            form = self.get_form_class()(instance=self.object)
        else:
            msg = 'Snippet not saved.'

        snippet.form = form
        t = loader.get_template(util.get_template_path("snippet/form.html"))
        c = RequestContext(self.request, {'snippet': snippet})
        resp = {
            'snippet_id': self.object.id,
            'status': status,
            'message': msg,
            'html': t.render(c),
            'warning': warning,
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    def form_valid(self, form):
        self.object = form.save()
        if self.request.is_ajax():
            return self.response_ajax(form, self.object, 200)
        return super(SnippetUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return self.response_ajax(form, self.object, 400)
        return super(SnippetUpdateView, self).form_invalid(form)


class SnippetDeleteView(LoginRequiredMixin, CsrfProtectMixin, TemplateView, ArticleHelperMixin):
    """
    Delete a snippet
    """
    template_name = '404.html'

    def get_next_snippet_id(self, snippet):
        snippets = Snippet.objects \
            .filter(article=snippet.article) \
            .filter(priority__gt=snippet.priority) \
            .order_by('priority')
        if not snippets:
            snippets = Snippet.objects \
                .filter(article=snippet.article) \
                .filter(priority__lt=snippet.priority) \
                .order_by('-priority')
        if snippets:
            return snippets[0].id
        return snippet.id

    def post(self, request, *args, **kwargs):
        snippet_id = self.kwargs.get('pk', None)
        snippet = get_object_or_404(Snippet, id=snippet_id)
        article = snippet.article
        next_snippet_id = self.get_next_snippet_id(snippet)
        snippet.delete()
        if self.request.is_ajax():
            self.prepare_snippets_for_article(article)
            t = loader.get_template(util.get_template_path("snippet/list.html"))
            c = RequestContext(self.request, {'article': article})
            resp = {
                'snippet_id': next_snippet_id,
                'status': 200,
                'message': "Snippet deleted.",
                'html': t.render(c),
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")
        return super(SnippetDeleteView, self).post(*args, **kwargs)


class SnippetSwapPriorityView(LoginRequiredMixin, CsrfProtectMixin, TemplateView, ArticleHelperMixin):
    """
    Reorder a snippet. Move up or down
    """
    template_name = '404.html'

    def get_next_snippet_by_priority_by_direction(self, snippet):
        self.direction = self.kwargs.get('direction', None)
        priority = snippet.priority
        if self.direction.upper() == 'DOWN':
            priority += 1
        elif self.direction.upper() == 'UP':
            priority -= 1

        snippets = Snippet.objects.filter(article=snippet.article, priority=priority)
        if snippets:
            return snippets[0]
        return None

    def swap_snippet_priority(self, snippet1, snippet2):
        """
        Swap priorities while handling db constrain on uniqueness.
        """
        snippet1_priority_cache = snippet1.priority
        snippet1.priority = random.randint(2000, 30000)
        snippet1.save()
        snippet1.priority, snippet2.priority = snippet2.priority, snippet1_priority_cache
        snippet2.save()
        snippet1.save()

    def post(self, request, *args, **kwargs):
        snippet_id = self.kwargs.get('pk', None)
        snippet1 = get_object_or_404(Snippet, id=snippet_id)
        snippet2 = self.get_next_snippet_by_priority_by_direction(snippet1)
        if snippet2 is not None:
            self.swap_snippet_priority(snippet1, snippet2)

        if self.request.is_ajax():
            self.prepare_snippets_for_article(snippet1.article)
            t = loader.get_template(util.get_template_path("snippet/list.html"))
            c = RequestContext(self.request, {'article': snippet1.article})
            resp = {
                'snippet_id': snippet_id,
                'status': 200,
                'message': "Snippet moved {}".format(self.direction),
                'html': t.render(c),
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")
        return super(SnippetSwapPriorityView, self).post(*args, **kwargs)
