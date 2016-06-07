from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.encoding import python_2_unicode_compatible

from .. import utils as util
from .. import defaults as defs


@python_2_unicode_compatible
class CommentCode(models.Model):

    COMMENT_PROVIDER_FACEBOOK = 'Facebook'
    COMMENT_PROVIDER_DISQUS = 'Disqus'
    COMMENT_PROVIDER_OPTIONS = (
        (COMMENT_PROVIDER_FACEBOOK, COMMENT_PROVIDER_FACEBOOK),
        (COMMENT_PROVIDER_DISQUS, COMMENT_PROVIDER_DISQUS),
    )

    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(
        max_length=30,
        default=COMMENT_PROVIDER_DISQUS,
        choices=COMMENT_PROVIDER_OPTIONS,
    )

    code = models.TextField(
        _("Comment Code"),
        blank=True,
        null=True,
        help_text=_('Third-party "Comment" Code. (e.g. Facebook, Disqus)'),
    )

    active = models.BooleanField(
        _('Active'),
        default=False,
        help_text=_('If Active comments are enabled.'),
    )

    def __str__(self):
        return 'Comment:{}'.format(self.id)

    def save(self, *args, **kwargs):
        if self.active:
            for code in self.__class__.objects.exclude(id=self.id):
                code.active = False
                code.save()
        super(CommentCode, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Comment')
        unique_together = (('name',))
