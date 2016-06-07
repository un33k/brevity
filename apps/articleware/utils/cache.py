from django.core.cache import cache

from .. import defaults as defs


def get_user_activity_cache_key(request, activity_type):
    cache_key = None
    if request.user.is_authenticated():
        cache_key = 'user_{}_activity_state_{}_{}'.format(activity_type, request.user.id, request.user.email)
    return cache_key.lower()


def set_user_activity_state(request, activity_type):
    """
    Records whether this user is actively editing articles of `activity_type`.
    """
    if request.user.is_authenticated():
        cache_key = get_user_activity_cache_key(request, activity_type)
        if cache_key:
            cache.set(cache_key, 'ON', defs.ARTICLEWARE_ACTIVITY_CACHE)


def is_user_active(request, activity_type):
    """
    If user has been actively editing articles, returns True otherwise False
    """
    active = False
    if request.user.is_authenticated():
        cache_key = get_user_activity_cache_key(request, activity_type)
        if cache_key:
            status = cache.get(cache_key)
            if status:
                active = True
    return active
