from django.conf import settings
from django.apps import apps
from django.db.models import signals
from django.db import DEFAULT_DB_ALIAS
from django.db import transaction
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType

import autocomplete_light.shortcuts as al

from .models import ContentTag
from .models import CategoryTag
from .models import TargetingTag
from .models import Article
from .models import Track

from . import defaults as defs


class CategoryTagAutocomplete(al.AutocompleteModelBase):
    limit_choices = 10
    order_by = (('name',))


class TargetingTagAutocomplete(al.AutocompleteModelBase):
    limit_choices = 10
    order_by = (('name',))


class ContentTagAutocomplete(al.AutocompleteModelBase):
    limit_choices = 10
    order_by = (('name',))


def post_migrate_receiver(app_config, verbosity=2, interactive=False, using=DEFAULT_DB_ALIAS, **kwargs):
    """
    Finalize the app.
    """


def register_autocomplete(verbosity=2):
    al.register(CategoryTag, CategoryTagAutocomplete)
    al.register(TargetingTag, TargetingTagAutocomplete)
    al.register(ContentTag, ContentTagAutocomplete)


def create_tracker(sender, instance, created, *args, **kwargs):
    """
    Create a tracker object upon article creation.
    """
    created = False
    try:
        obj = Track.objects.get(article=instance)
    except Track.DoesNotExist:
        try:
            with transaction.atomic():
                obj = Track.objects.create(article=instance)
                created = True
        except IntegrityError:
            obj = Track.objects.get(article=instance)


def article_trac_on_create(sender, instance, **kwargs):
    """
    Increment trac records for article.
    """
    article_ctype = ContentType.objects.get_for_model(Article)
    if instance.content_type == article_ctype:
        obj = instance.content_object
        if instance.trac_type == instance.TRACWARE_TYPE_LIKE:
            obj.track.set_like(increment=True)
        obj.save()


def article_trac_on_delete(sender, instance, **kwargs):
    """
    Decrement trac records for article.
    """
    article_ctype = ContentType.objects.get_for_model(Article)
    if instance.content_type == article_ctype:
        obj = instance.content_object
        if instance.trac_type == instance.TRACWARE_TYPE_LIKE:
            obj.track.set_like(increment=False)
        obj.save()
