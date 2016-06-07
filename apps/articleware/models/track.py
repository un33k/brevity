import os

from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from django.utils.encoding import python_2_unicode_compatible

from .. import utils as util
from .. import defaults as defs


@python_2_unicode_compatible
class Track(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    article = models.OneToOneField(
        'article',
        related_name="%(class)s",
        editable=False,
    )

    hit = models.PositiveIntegerField(
        default=0,
        editable=False,
    )

    view = models.PositiveIntegerField(
        default=0,
        editable=False,
    )

    like = models.PositiveIntegerField(
        default=0,
        editable=False,
    )

    def __str__(self):
        return 'article:{} [l:{}, v:{}]'.format(self.article.id, self.like, self.view)

    @property
    def up_hits(self):
        self.hit += 1
        self.save()
        return self.hit

    @property
    def up_views(self):
        self.view += 1
        self.save()
        return self.view

    def set_like(self, increment=True):
        if increment:
            self.like += 1
        elif self.like > 0:
            self.like -= 1
        self.save()
        return self.like
