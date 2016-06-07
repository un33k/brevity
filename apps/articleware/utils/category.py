from django.db.models import Count
from django.core.cache import cache
from django.db import models

from ..models import CategoryTag
from .. import defaults as defs
from .common import get_approved_writer_group_name


def get_category_cache_key():
    cache_key = 'articleware_get_active_categories'
    return cache_key


def get_multi_category_cache_key():
    cache_key = 'articleware_has_multiple_active_categories'
    return cache_key


def get_active_categories(request=None):
    """
    Returns a list of categories sorted by most number of reference.
    """
    cache_key = get_category_cache_key()
    categories = cache.get(cache_key)
    if categories:
        return categories

    from ..models import Article

    query = models.Q()
    query &= models.Q(article__author__is_active=True)
    query &= models.Q(article__status=Article.ARTICLE_STATUS_PUBLIC)
    query &= models.Q(article__flavor=Article.ARTICLE_FLAVOR_ARTICLE)

    approved_group = get_approved_writer_group_name()
    approved_query = models.Q(article__author__groups__name=approved_group)
    if request and request.user.is_authenticated():
        approved_query |= Q(author=request.user)
    query &= approved_query

    categories = CategoryTag.objects.annotate(
        count=models.Sum(
            models.Case(
                models.When(
                    query,
                    then=1
                ),
                default=0,
                output_field=models.IntegerField()
            )
        )
    ).filter(count__gt=0).order_by('-count', 'name')

    cache.set(cache_key, categories, defs.ARTICLEWARE_ACTIVE_CATEGORY_CACHE)
    return categories


def has_multiple_active_categories(request):
    """
    Returns True if site has articles in multiple categories, else return False
    """
    cache_key = get_multi_category_cache_key()
    multiple = cache.get(cache_key)
    if multiple is not None:
        return multiple
    multiple = True if len(get_active_categories()) > 1 else False
    cache.set(cache_key, multiple, defs.ARTICLEWARE_ACTIVE_CATEGORY_CACHE)
    return multiple
