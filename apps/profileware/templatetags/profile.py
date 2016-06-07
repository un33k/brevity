from django import template
from django.conf import settings

from social.apps.django_app.default.models import UserSocialAuth

register = template.Library()


@register.filter
def has_social_association(request, provider):
    """
    Returns True if profile has social association to this provider.
    """
    try:
        UserSocialAuth.objects.get(user=request.user, provider__iexact=provider)
    except UserSocialAuth.DoesNotExist:
        return False
    return True
