import os
from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from django.core.files.storage import get_storage_class
from django.contrib.staticfiles.storage import staticfiles_storage
from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_delete
from django.core.files.base import ContentFile
from django.utils.encoding import python_2_unicode_compatible

from .. import utils as util
from .. import defaults as defs

DefaultStorage = get_storage_class(defs.ARTICLEWARE_STORAGE_CLASS)


@python_2_unicode_compatible
class Video(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    snippet = models.ForeignKey(
        'Snippet',
        related_name="%(class)s",
        null=False,
    )

    image = models.URLField(
        _('Image URL'),
        max_length=256,
    )

    link = models.URLField(
        _('Video URL'),
        max_length=256,
    )

    provider = models.CharField(
        max_length=100,
    )

    vid = models.CharField(
        max_length=100,
    )

    priority = models.PositiveSmallIntegerField(
        null=True,
        editable=False,
    )

    class Meta:
        verbose_name = _('video')
        verbose_name_plural = _('videos')
        unique_together = (('snippet', 'vid'), ('snippet', 'vid', 'priority'))

    def __str__(self):
        return '{}-{}'.format(self.provider, self.vid)

    @property
    def is_video(self):
        return True

    @property
    def default_image(self):
        if self.image:
            return self.image
        try:
            url = staticfiles_storage.url('img/misc/image-not-found.jpg')
        except ValueError:  # no access to cdn @ this time
            url = '#'
        return url

    def thumb(self):
        if self.image:
            url = self.image
        else:
            try:
                url = staticfiles_storage.url('img/misc/image-not-found.jpg')
            except ValueError:  # no access to cdn @ this time
                url = '#'
        return u'<a href="{0}" target="_blank"><img src="{0}" width=120 height=68/></a>'.format(url)
    thumb.allow_tags = True
