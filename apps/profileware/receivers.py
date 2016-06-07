from django.db import transaction
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType

from .models import Track
from .models import UserProfile
from . import defaults as defs


def create_tracker(sender, instance, created, *args, **kwargs):
    """
    Create a tracker object upon profile creation.
    """
    created = False
    try:
        obj = Track.objects.get(profile=instance)
    except Track.DoesNotExist:
        try:
            with transaction.atomic():
                obj = Track.objects.create(profile=instance)
                created = True
        except IntegrityError:
            obj = Track.objects.get(profile=instance)


def profile_trac_on_create(sender, instance, **kwargs):
    """
    Increment trac records for UserProfile.
    """
    profile_ctype = ContentType.objects.get_for_model(UserProfile)
    if instance.content_type == profile_ctype:
        obj = instance.content_object
        if instance.trac_type == instance.TRACWARE_TYPE_STAR:
            obj.track.set_star(increment=True)
        obj.save()


def profile_trac_on_delete(sender, instance, **kwargs):
    """
    Decrement trac records for UserProfile.
    """
    profile_ctype = ContentType.objects.get_for_model(UserProfile)
    if instance.content_type == profile_ctype:
        obj = instance.content_object
        if instance.trac_type == instance.TRACWARE_TYPE_STAR:
            obj.track.set_star(increment=False)
        obj.save()
