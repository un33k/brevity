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

    profile = models.OneToOneField(
        'UserProfile',
        related_name="%(class)s",
        editable=False,
    )

    view = models.PositiveIntegerField(
        default=0,
        editable=False,
    )

    star = models.PositiveIntegerField(
        default=0,
        editable=False,
    )

    def __str__(self):
        return 'profile:{} [s:{}, v:{}]'.format(self.profile.id, self.star, self.view)

    @property
    def up_views(self):
        self.view += 1
        self.save()
        return self.view

    def set_star(self, increment=True):
        if increment:
            self.star += 1
        elif self.star > 0:
            self.star -= 1
        self.save()
        return self.star
