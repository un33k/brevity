import os
from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from django.core.files.storage import get_storage_class
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.encoding import python_2_unicode_compatible
from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_delete
from django.core.files.base import ContentFile

from .. import utils as util
from .. import defaults as defs

DefaultStorage = get_storage_class(defs.ARTICLEWARE_STORAGE_CLASS)


@python_2_unicode_compatible
class Image(models.Model):
    default_storage = DefaultStorage()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    snippet = models.ForeignKey(
        'Snippet',
        related_name="%(class)s",
        null=False,
    )

    image = models.ImageField(
        null=True,
        storage=default_storage,
        upload_to=util.uploadto_image_to_year_month_uuid_lg,
        max_length=255,
    )

    image_md = models.ImageField(
        null=True,
        storage=default_storage,
        upload_to=util.uploadto_image_to_year_month_uuid_md,
        max_length=255,
    )

    image_sm = models.ImageField(
        null=True,
        storage=default_storage,
        upload_to=util.uploadto_image_to_year_month_uuid_sm,
        max_length=255,
    )

    priority = models.PositiveSmallIntegerField(
        null=True,
        editable=False,
    )

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
        unique_together = (('snippet', 'priority'))

    def __str__(self):
        return self.image.name

    def remove_old_files(self):
        if defs.ARTICLEWARE_REMOVE_IMAGE_CACHE_ON_DELETION:
            try:
                obj = Image.objects.get(id=self.id)
            except Image.DoesNotExist:
                return
            if obj.image and self.image and obj.image != self.image:
                obj.image.delete()
            if obj.image_md and self.image_md and obj.image_md != self.image_md:
                obj.image_md.delete()
            if obj.image_sm and self.image_sm and obj.image_sm != self.image_sm:
                obj.image_sm.delete()

    def save(self, *args, **kwargs):
        self.remove_old_files()
        return super(Image, self).save(*args, **kwargs)

    @property
    def is_image(self):
        return True

    @property
    def basename(self):
        return os.path.basename(self.image.url)

    @property
    def default_image(self):
        if self.image:
            return self.image.url
        try:
            url = staticfiles_storage.url('img/misc/image-not-found.jpg')
        except ValueError:  # no access to cdn @ this time
            url = '#'
        return url

    def thumb(self):
        if self.image:
            url = self.image.url
        else:
            try:
                url = staticfiles_storage.url('img/misc/image-not-found.jpg')
            except ValueError:  # no access to cdn @ this time
                url = '#'
        return u'<a href="{0}" target="_blank"><img src="{0}" width=120 height=68/></a>'.format(url)
    thumb.allow_tags = True


@receiver(pre_delete, sender=Image)
def _image_enforce_single_and_bulk_delete(sender, instance, **kwargs):
    if defs.ARTICLEWARE_REMOVE_IMAGE_CACHE_ON_DELETION:
        if instance.image:
            instance.image.delete()
        if instance.image_md:
            instance.image_md.delete()
        if instance.image_sm:
            instance.image_sm.delete()
