from django import template

from .. import defaults as defs
from .. import utils as util

register = template.Library()


@register.filter
def is_article_admin(request):
    """
    Given a request, it returns True of user is an article admin.
    """
    article_admin = util.is_article_admin(request)
    return article_admin


@register.filter
def is_blog_admin(request):
    """
    Given a request, it returns True of user is a blog admin.
    """
    blog_admin = util.is_article_blog_admin(request)
    return blog_admin


@register.filter
def is_page_admin(request):
    """
    Given a request, it returns True of user is a page admin.
    """
    page_admin = util.is_article_page_admin(request)
    return page_admin
