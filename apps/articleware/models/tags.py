from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager
from taggit.models import TagBase as Taggit_TagBase
from taggit.models import GenericTaggedItemBase

from slugify import slugify as slugit

from toolware.utils.query import CaseInsensitiveManager


class TagBase(Taggit_TagBase):
    def slugify(self, tag, i=None):
        tag = '{}-{}'.format(tag, i) if i else tag
        slug = slugit(tag)
        return slug

    class Meta:
        abstract = True


class ContentTag(TagBase):
    """
    Content grouping details for a particular article.
    """
    objects = CaseInsensitiveManager()
    CASE_INSENSITIVE_FIELDS = ['name', 'slug']

    class Meta:
        verbose_name = _("Content Tag")
        verbose_name_plural = _("Content Tags")


class ContentTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(
        ContentTag,
        related_name="%(app_label)s_%(class)s_items"
    )


class CategoryTag(TagBase):
    """
    Category grouping for a particular article.
    """
    objects = CaseInsensitiveManager()
    CASE_INSENSITIVE_FIELDS = ['name', 'slug']

    class Meta:
        verbose_name = _("Category Tag")
        verbose_name_plural = _("Category Tags")


class CategoryTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(
        CategoryTag,
        related_name="%(app_label)s_%(class)s_items"
    )


class TargetingTag(TagBase):
    """
    Geographical grouping for a particular article.
    """
    objects = CaseInsensitiveManager()
    CASE_INSENSITIVE_FIELDS = ['name', 'slug']

    class Meta:
        verbose_name = _("Targeting Tag")
        verbose_name_plural = _("Targeting Tags")


class TargetingTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(
        TargetingTag,
        related_name="%(app_label)s_%(class)s_items"
    )
