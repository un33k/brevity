from django import template
from django.core.cache import cache

from ipware.ip import get_ip
from ipware.ip import get_real_ip

from .. import defaults as defs

register = template.Library()


@register.filter
def hit_count(request, article):
    """
    Given a request and an article object, it increments hit count and returns the result.
    It only increments it once per session.
    """
    cache_key = _get_cache_key(request, article, 'hit')
    already_tracked = cache.get(cache_key)
    if already_tracked:
        hit = article.track.hit
    else:
        hit = article.track.up_hits
        cache.set(cache_key, '1', defs.ARTICLEWARE_ARTICLE_HIT_CACHE_TIMEOUT_MINUTES)
    return hit


@register.filter
def view_count(request, article):
    """
    Given a request and an article object, it increments view count and returns the result.
    It only increments it once per session.
    """
    cache_key = _get_cache_key(request, article, 'view')
    already_tracked = cache.get(cache_key)
    if already_tracked:
        view = article.track.view
    else:
        view = article.track.up_views
        cache.set(cache_key, '1', defs.ARTICLEWARE_ARTICLE_HIT_CACHE_TIMEOUT_MINUTES)
    return view


def _get_cache_key(request, obj, type):
    """
    Get a cache key for the operation.
    For anonymous we trigger a session creation instead of setting `SESSION_SAVE_EVERY_REQUEST = True`
    which updates the session on each request.
    """
    if request.user.is_authenticated():
        unique_id = '{}{}'.format(request.session.session_key[:75], request.session.session_key[-75:])
    else:
        if not hasattr(request, 'session'):
            unique_id = get_real_ip(request) or get_ip(request)
        else:
            if not request.session.session_key:
                request.session.save()
                request.session.modified = True
            unique_id = request.session.session_key

    cache_key = '{}:{}:{}:{}'.format(
        obj.__class__.__name__,
        type,
        unique_id,
        obj.id
    )
    return cache_key[:254]  # memcache key is 255
