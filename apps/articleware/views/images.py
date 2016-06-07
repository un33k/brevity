import os
import json
import random
import requests

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

from pilkit.lib import StringIO
from pilkit.processors import ResizeToFill

from toolware.utils.mixin import LoginRequiredMixin
from toolware.utils.mixin import CsrfProtectMixin
from toolware.utils.mixin import DeleteMixin

from ..models import Snippet
from ..models import Image
from ..forms import ImageForm

from .. import utils as util
from .. import defaults as defs
from .common import *


class ImageAddView(LoginRequiredMixin, CsrfProtectMixin, TemplateView, ArticleHelperMixin):
    """
    Add an snippet image.
    """
    template_name = '404.html'

    def get_image_info(self):
        """
        If link to image is provides, we download the image from the link.
        """
        success = False
        messages = {
            'max_file_size': 'Failed to add image. Max size is {} MB'.format(defs.ARTICLEWARE_MAX_IMAGE_SIZE),
            'invalid_link': 'Invalid image link.',
            'unknown_file': 'Not an image link.',
            'download_error': "Failed to get file from link.",
        }
        info = {
            'file': None,
            'name': '',
            'ext': '',
            'msg': ''
        }

        file = self.request.FILES.get('file')
        if file:
            if self.is_valid_size(file.size):
                base, ext = os.path.splitext(file.name)
                info['file'] = file.read()
                info['name'] = '{}_{}{}'.format(base, self.snippet.id, ext)
                info['ext'] = ext
                success = True
            else:
                info['msg'] = messages['max_file_size']
        else:
            image_url = self.request.POST.get('image_url', '').strip()
            if image_url:
                extention = self.get_extention(image_url)
                if extention:
                    content_size = self.get_content_length(image_url)
                    if self.is_valid_size(content_size):
                        success, resp = self.do_get_request(image_url, stream=True)
                        if success:
                            info['file'] = resp.content
                            info['name'] = 'image_{}.{}'.format(self.snippet.id, extention)
                            info['ext'] = '.{}'.format(extention)
                        else:
                            error = self.get_message()
                            info['msg'] = '{}'.format(error or messages['download_error'])
                    else:
                        info['msg'] = messages['max_file_size']
                else:
                    error = self.get_message()
                    info['msg'] = '{}'.format(error or messages['invalid_link'])
            else:
                info['msg'] = messages['invalid_link']
        return info, success

    def upload_image(self, count):
        uploaded = False
        msg = 'Image added.'

        info, success = self.get_image_info()
        if success:
            processor_name = self.request.POST.get('process_type', defs.ARTICLEWARE_ACTIVE_IMAGE_PROCESSORS[0])
            processor_func = defs.ARTICLEWARE_AVAILABLE_IMAGE_PROCESSORS.get(processor_name, ResizeToFill)

            res = defs.ARTICLEWARE_RESOLUTIONS['enabled']
            fname = info['name']
            fdata = StringIO(info['file'])

            format = res['lg']['format']
            quality = res['lg']['quality']
            width, height = res['lg']['width'], res['lg']['height']
            f_lg = self.process_image(fname, fdata, format, width, height, processor_func, quality)

            format = res['md']['format']
            quality = res['md']['quality']
            width, height = res['md']['width'], res['md']['height']
            f_md = self.process_image(fname, fdata, format, width, height, processor_func, quality)

            format = res['sm']['format']
            quality = res['sm']['quality']
            width, height = res['sm']['width'], res['sm']['height']
            f_sm = self.process_image(fname, fdata, format, width, height, processor_func, quality)

            self.image = Image(snippet=self.snippet, image=f_lg, image_md=f_md, image_sm=f_sm)
            self.image.priority = count + 1
            self.image.save()
            uploaded = True
        else:
            msg = info['msg']
        return uploaded, msg

    def post(self, *args, **kwargs):
        self.snippet = get_object_or_404(Snippet, id=self.request.POST.get('snippet'))
        count = Image.objects.filter(snippet=self.snippet).count()
        if count < defs.ARTICLEWARE_MAX_IMAGES_PER_SNIPPET:
            uploaded, msg = self.upload_image(count)
            if uploaded:
                self.prepare_images_for_snippet(self.snippet)
                t = loader.get_template(util.get_template_path("image/list.html"))
                c = RequestContext(self.request, {'snippet': self.snippet})
                resp = {
                    'snippet_id': self.snippet.id,
                    'image_id': self.image.id,
                    'image_name': self.image.basename,
                    'status': 201,
                    'message': msg,
                    'html': t.render(c),
                }
                return HttpResponseImageCreated(json.dumps(resp), content_type="application/json")
            else:
                resp = {
                    'snippet_id': self.snippet.id,
                    'status': 400,
                    'message': msg,
                }
            return HttpResponseBadRequest(json.dumps(resp), content_type="application/json")
        else:
            resp = {
                'snippet_id': self.snippet.id,
                'status': 400,
                'message': 'Max number of images per snippet is {}.'.format(
                    defs.ARTICLEWARE_MAX_IMAGES_PER_SNIPPET)
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")


class ImageDeleteView(LoginRequiredMixin, CsrfProtectMixin, TemplateView, ArticleHelperMixin):
    """
    Delete an snippet image.
    """
    template_name = '404.html'

    def post(self, *args, **kwargs):
        image_id = self.kwargs.get('pk')
        image = get_object_or_404(Image, id=image_id)
        snippet = image.snippet
        image.delete()
        self.prepare_images_for_snippet(snippet)
        t = loader.get_template(util.get_template_path("image/list.html"))
        c = RequestContext(self.request, {'snippet': snippet})
        resp = {
            'snippet_id': snippet.id,
            'image_id': image_id,
            'status': 200,
            'message': 'Image deleted.',
            'html': t.render(c),
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")


class ImageSwapPriorityView(LoginRequiredMixin, CsrfProtectMixin, TemplateView, ArticleHelperMixin):
    """
    Reorder an image. Move up or down
    """
    template_name = '404.html'

    def get_next_image_by_priority_by_direction(self, image):
        self.direction = self.kwargs.get('direction', None)
        priority = image.priority
        if self.direction.upper() == 'DOWN':
            priority += 1
        elif self.direction.upper() == 'UP':
            priority -= 1

        images = Image.objects.filter(snippet=image.snippet, priority=priority)
        if images:
            return images[0]
        return None

    def swap_snippet_priority(self, image1, image2):
        """
        Swap priorities while handling db constrain on uniqueness.
        """
        image1_priority_cache = image1.priority
        image1.priority = random.randint(2000, 30000)
        image1.save()
        image1.priority, image2.priority = image2.priority, image1_priority_cache
        image2.save()
        image1.save()

    def post(self, request, *args, **kwargs):
        image_id = self.kwargs.get('pk', None)
        image1 = get_object_or_404(Image, id=image_id)
        image2 = self.get_next_image_by_priority_by_direction(image1)
        if image2 is not None:
            self.swap_snippet_priority(image1, image2)

        snippet = image1.snippet
        self.prepare_images_for_snippet(snippet)
        t = loader.get_template(util.get_template_path("image/list.html"))
        c = RequestContext(self.request, {'snippet': snippet})
        resp = {
            'snippet_id': snippet.id,
            'image_id': image_id,
            'status': 200,
            'message': "Image moved {}".format(self.direction),
            'html': t.render(c),
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")
