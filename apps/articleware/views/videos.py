import os
import io
import json
import random
import requests

from django.core.files import File
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

from toolware.utils.mixin import LoginRequiredMixin
from toolware.utils.mixin import CsrfProtectMixin
from toolware.utils.mixin import DeleteMixin

from ..models import Snippet
from ..models import Video
from ..forms import VideoForm

from .. import utils as util
from .. import defaults as defs
from .common import *


class VideoAddView(LoginRequiredMixin, CsrfProtectMixin, TemplateView, ArticleHelperMixin):
    """
    Creates new video for a snippet.
    """
    template_name = '404.html'

    def response_ajax(self, status, msg='Video saved.'):
        resp = {
            'status': status,
            'message': msg,
        }

        if status == 201:
            self.prepare_videos_for_snippet(self.snippet)
            t = loader.get_template(util.get_template_path("video/list.html"))
            c = RequestContext(self.request, {'snippet': self.snippet})
            resp['html'] = t.render(c)

        return HttpResponse(json.dumps(resp), content_type="application/json")

    def create_video(self, info, count):
        priority = count + 1
        if info and info['thumb']:
            obj = Video(snippet=self.snippet, vid=info['vid'], image=info['thumb'],
                link=info['link'], provider=info['name'], priority=priority)
            obj.save()
            msg = "Video saved."
        return self.response_ajax(201, msg)

    def post(self, *args, **kwargs):
        self.snippet = get_object_or_404(Snippet, id=self.request.POST.get('snippet'))

        count = Video.objects.filter(snippet=self.snippet).count()
        if count >= defs.ARTICLEWARE_MAX_VIDEOS_PER_SNIPPET:
            msg = "Max number of videos per snippet is {}".format(defs.ARTICLEWARE_MAX_VIDEOS_PER_SNIPPET)
            return self.response_ajax(400, msg)

        found, info = util.get_video_info(self.request.POST.get('link'))
        if not found:
            return self.response_ajax(400, info['msg'])

        try:
            obj = Video.objects.get(snippet=self.snippet, vid=info['vid'])
            msg = "Video link already in the list."
            return self.response_ajax(400, msg)
        except Video.DoesNotExist:
            pass
        return self.create_video(info, count)


class VideoDeleteView(LoginRequiredMixin, CsrfProtectMixin, TemplateView, ArticleHelperMixin):
    """
    Delete an snippet video.
    """
    template_name = '404.html'

    def post(self, *args, **kwargs):
        video_id = self.kwargs.get('pk')
        video = get_object_or_404(Video, id=video_id)
        snippet = video.snippet
        video.delete()
        self.prepare_videos_for_snippet(snippet)
        t = loader.get_template(util.get_template_path("video/list.html"))
        c = RequestContext(self.request, {'snippet': snippet})
        resp = {
            'snippet_id': snippet.id,
            'video_id': video_id,
            'status': 200,
            'message': 'Video deleted.',
            'html': t.render(c),
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")


class VideoSwapPriorityView(LoginRequiredMixin, CsrfProtectMixin, TemplateView, ArticleHelperMixin):
    """
    Reorder an video. Move up or down
    """
    template_name = '404.html'

    def get_next_video_by_priority_by_direction(self, video):
        self.direction = self.kwargs.get('direction', None)
        priority = video.priority
        if self.direction.upper() == 'DOWN':
            priority += 1
        elif self.direction.upper() == 'UP':
            priority -= 1

        videos = Video.objects.filter(snippet=video.snippet, priority=priority)
        if videos:
            return videos[0]
        return None

    def swap_snippet_priority(self, video1, video2):
        """
        Swap priorities while handling db constrain on uniqueness.
        """
        video1_priority_cache = video1.priority
        video1.priority = random.randint(2000, 30000)
        video1.save()
        video1.priority, video2.priority = video2.priority, video1_priority_cache
        video2.save()
        video1.save()

    def post(self, request, *args, **kwargs):
        video_id = self.kwargs.get('pk', None)
        video1 = get_object_or_404(Video, id=video_id)
        video2 = self.get_next_video_by_priority_by_direction(video1)
        if video2 is not None:
            self.swap_snippet_priority(video1, video2)

        snippet = video1.snippet
        self.prepare_videos_for_snippet(snippet)
        t = loader.get_template(util.get_template_path("video/list.html"))
        c = RequestContext(self.request, {'snippet': snippet})
        resp = {
            'snippet_id': snippet.id,
            'video_id': video_id,
            'status': 200,
            'message': "Video moved {}".format(self.direction),
            'html': t.render(c),
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")
