from django.db import models
from django.conf import settings
from django.core import validators

from django.utils.translation import gettext as _
from django.utils.encoding import python_2_unicode_compatible

from .. import utils as util
from .. import defaults as defs


@python_2_unicode_compatible
class Snippet(models.Model):
    """
    Snippet Item class.
    One or more snippets can be attached to an article.
    """
    SNIPPET_TYPE_TEXT = 'TEXT'
    SNIPPET_TYPE_IMAGE = 'IMAGE'
    SNIPPET_TYPE_VIDEO = 'VIDEO'
    SNIPPET_TYPE_MAP = 'MAP'
    SNIPPET_TYPE_OPTIONS = (
        (SNIPPET_TYPE_TEXT, SNIPPET_TYPE_TEXT),
        (SNIPPET_TYPE_IMAGE, SNIPPET_TYPE_IMAGE),
        (SNIPPET_TYPE_VIDEO, SNIPPET_TYPE_VIDEO),
        (SNIPPET_TYPE_MAP, SNIPPET_TYPE_MAP),
    )
    image_processors = defs.ARTICLEWARE_ACTIVE_IMAGE_PROCESSORS

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    article = models.ForeignKey(
        'Article',
        related_name="%(class)s",
        null=False,
    )

    type = models.CharField(
        max_length=10,
        default=SNIPPET_TYPE_IMAGE,
        choices=SNIPPET_TYPE_OPTIONS,
    )

    priority = models.PositiveSmallIntegerField(
        null=True,
        editable=False,
    )

    caption = models.TextField(
        _("caption"),
        null=True,
        blank=True,
        validators=[validators.MaxLengthValidator(110)],
        help_text=_("Brief explanation & photo/video credit appended to this snippet.")
    )

    content = models.TextField(
        _("content"),
        null=True,
        blank=True,
        validators=[validators.MaxLengthValidator(10000)],
        help_text=_("Content for this snippet.")
    )

    class Meta:
        verbose_name = _('snippet')
        verbose_name_plural = _('snippets')
        unique_together = (('article', 'priority'))

    def __str__(self):
        return u'{}-s{}-a{}'.format(self.type, self.id, self.article.id)

    @property
    def images(self):
        """
        Returns all related images from this snippet
        """
        images = self.image.all().order_by('priority', '-created_at')
        return images

    @property
    def videos(self):
        """
        Returns all related videos for this snippet
        """
        videos = self.video.all().order_by('priority', '-created_at')
        return videos

    @property
    def is_ready(self):
        """
        Returns True if snippet has warnings.
        Ex: Empty text, no image or video etc.
        """
        if self.type == self.SNIPPET_TYPE_TEXT:
            if not self.content or len(self.content) < 1:
                return False
        elif self.type == self.SNIPPET_TYPE_IMAGE:
            if self.images.count() < 1:
                return False
        elif self.type == self.SNIPPET_TYPE_VIDEO:
            if self.videos.count() < 1:
                return False
        return True
