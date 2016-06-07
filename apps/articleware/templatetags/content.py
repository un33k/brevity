from django import template
from django.conf import settings

from .. import defaults as defs
from ..utils import strip_all_tags
from ..utils import get_article_public_short_url
from ..utils import securify_external_links

register = template.Library()


@register.filter
def textify(html):
    """
    Given an html content, it returns a text version.
    """
    disallowed_tags = defs.ARTICLEWARE_DISALLOWED_TAGS + defs.ARTICLEWARE_TABLE_TAGS
    text = strip_all_tags(html, disallowed_tags)
    return text


@register.filter
def pub_short_link(request, article):
    """
    Given a request and an article, it returns the fully qualified short public URL.
    """
    url = get_article_public_short_url(request, article)
    return url


@register.filter
def securify(html, request):
    """
    Given an html content, it returns a version with all http links redirected to https.
    """
    is_secure = getattr(settings, 'DEBUG_SECURIFY_URLS',
        getattr(settings, 'SITE_PROTOCOL', request.is_secure()))
    html = securify_external_links(html, is_secure)
    return html
