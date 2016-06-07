import requests

from django.http import HttpResponse
from django.core.files.uploadedfile import SimpleUploadedFile

from pilkit.lib import StringIO
from pilkit.lib import Image as PilImage
from pilkit.processors import ProcessorPipeline
from pilkit.processors import ResizeToFill
from pilkit.processors import Transpose

from ..models import Snippet
from ..models import Image
from ..models import Video
from ..forms import SnippetTextForm
from ..forms import SnippetImageForm
from ..forms import SnippetVideoForm
from ..forms import SnippetMapForm
from ..forms import VideoForm

from .. import defaults as defs


class HttpResponseBadRequest(HttpResponse):
    status_code = 400


class HttpResponseImageCreated(HttpResponse):
    status_code = 201


class HttpResponseImageDeleted(HttpResponse):
    status_code = 200


class HeadRequest(object):

    request_message = ''
    request_session = requests.Session()
    request_headers = {}
    request_timeout = defs.ARTICLEWARE_CONNECTION_REQUEST_TIMEOUT
    request_params = {
        'User-Agent': '{} Agent Version {}'.format(defs.ARTICLEWARE_REFERER, defs.ARTICLEWARE_ASSET_VERSION),
        'referrer': defs.ARTICLEWARE_REFERER,
    }

    def get_message(self):
        return self.request_message

    def do_head_request(self, image_url):
        if not self.request_headers:
            try:
                resp = self.request_session.head(image_url,
                    headers=self.request_params, timeout=self.request_timeout)
            except requests.exceptions.Timeout:
                self.request_message = 'Timed out.'
            except requests.exceptions.TooManyRedirects:
                self.request_message = 'Too Many Redirects.'
            except requests.exceptions.RequestException:
                self.request_message = 'Failed to connect.'
            else:
                if resp.status_code == 200:
                    self.request_headers = resp.headers
        return self.request_headers

    def do_get_request(self, image_url, stream=False):
        success = False
        try:
            resp = self.request_session.get(image_url, stream=stream,
                headers=self.request_params, timeout=self.request_timeout)
        except requests.exceptions.Timeout:
            self.request_message = 'Timed out.'
        except requests.exceptions.TooManyRedirects:
            self.request_message = 'Too Many Redirects.'
        except requests.exceptions.RequestException:
            self.request_message = 'Failed to connect.'
        else:
            if resp.status_code == 200:
                success = True
        return success, resp

    def get_content_type(self, image_url):
        mimetype = None
        headers = self.do_head_request(image_url)
        if not headers:
            return mimetype
        content_type = headers.get('content-type', '')
        try:
            mimetype = content_type.split(';')[0].lower()
        except KeyError:
            pass
        return mimetype

    def get_content_length(self, image_url):
        size = None
        headers = self.do_head_request(image_url)
        if not headers:
            return size
        size = headers.get('content-length')
        return size

    def get_extension_from_type(self, type_string):
        if type(type_string) == str or type(type_string) == unicode:
            temp = type_string.split('/')
            if len(temp) >= 2:
                return temp[1]
            elif len(temp) >= 1:
                return temp[0]
            else:
                return None

    def get_extention(self, image_url):
        content_type = self.get_content_type(image_url)
        if content_type in defs.ARTICLEWARE_VALID_IMAGE_FORMATS:
            return self.get_extension_from_type(content_type)
        return None

    def is_valid_size(self, size):
        if size and int(size) < defs.ARTICLEWARE_MAX_IMAGE_SIZE * 1024 * 1024:
            return True
        return False


class ArticleHelperMixin(HeadRequest):
    """
    Renders all snippets for in-place whole element replacement."
    """
    def prepare_snippets_for_article(self, article):
        """
        Prepares snippets for an article during creation/editing of an article.
        """
        self.reorder_snippets_for_article(article)
        snippet_list = []
        for snippet in article.snippets:
            if snippet.type == snippet.SNIPPET_TYPE_TEXT:
                snippet.form = SnippetTextForm(instance=snippet)
            elif snippet.type == snippet.SNIPPET_TYPE_IMAGE:
                self.prepare_images_for_snippet(snippet)
                snippet.form = SnippetImageForm(instance=snippet)
            elif snippet.type == snippet.SNIPPET_TYPE_VIDEO:
                self.prepare_videos_for_snippet(snippet)
                snippet.form = SnippetVideoForm(instance=snippet)
            elif snippet.type == snippet.SNIPPET_TYPE_MAP:
                snippet.form = SnippetMapForm(instance=snippet)
            snippet_list.append(snippet)

        if snippet_list:
            snippet_list[0].no_swap_down = True
            snippet_list[-1].no_swap_up = True
        article.unfinal_snippets = snippet_list

    def prepare_images_for_snippet(self, snippet):
        """
        Prepares images for a snippet during creation/editing of an article.
        """
        self.reorder_images_for_snippets(snippet)
        image_list = []
        for image in snippet.images:
            image_list.append(image)
        if image_list:
            image_list[0].no_swap_down = True
            image_list[-1].no_swap_up = True
        snippet.unfinal_images = image_list

    def prepare_videos_for_snippet(self, snippet):
        """
        Prepares videos for a snippet during creation/editing of an article.
        """
        video_list = []
        self.reorder_videos_for_snippets(snippet)
        for video in snippet.videos:
            video_list.append(video)
        if video_list:
            video_list[0].no_swap_down = True
            video_list[-1].no_swap_up = True
        snippet.unfinal_videos = video_list

    def reorder_snippets_for_article(self, article):
        count = 1
        for snippet in article.snippets:
            snippet.priority = count
            try:
                snippet.save()
            except FileNotFoundError:
                pass
            count += 1

    def reorder_images_for_snippets(self, snippet):
        count = 1
        for image in snippet.images:
            image.priority = count
            try:
                image.save()
            except FileNotFoundError:
                pass
            count += 1

    def reorder_videos_for_snippets(self, snippet):
        count = 1
        for video in snippet.videos:
            video.priority = count
            try:
                video.save()
            except FileNotFoundError:
                pass
            count += 1

    def process_image(self, name, content, format, width, height, processor=None, quality=100):
        if processor is None:
            processor = ResizeToFill
        img = PilImage.open(content)
        pipeline = ProcessorPipeline([Transpose(), processor(width, height)])
        img = pipeline.process(img)
        newfile = StringIO()
        img.save(newfile, format=format, quality=quality)
        newfile.seek(0)
        suf = SimpleUploadedFile(name, newfile.read(), content_type='JPEG')
        return suf
