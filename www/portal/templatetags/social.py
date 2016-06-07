from django.conf import settings
from django import template
from django.contrib.staticfiles.storage import staticfiles_storage

from toolware.compat import quote
from articleware.utils import get_article_public_short_url

register = template.Library()


def _get_url_title(request, article):
    """
    Given an article object, it returns a tuple (full_short_url, title)
    """
    url = get_article_public_short_url(request, article)
    return quote(url), quote(article.headline)


@register.filter
def facebook_share(request, article):
    """
    Given a request, an article, it returns a facebook share url.
    """
    link, title = _get_url_title(request, article)
    url = 'https://www.facebook.com/sharer/sharer.php?u={}'.format(link)
    return url


@register.filter
def twitter_share(request, article):
    """
    Given a request, an article, it returns a twitter share url.
    """
    link, title = _get_url_title(request, article)
    url = 'https://twitter.com/intent/tweet?url={}&text={}'.format(link, title)
    return url


@register.filter
def google_share(request, article):
    """
    Given a request, an article, it returns a google share url.
    """
    link, title = _get_url_title(request, article)
    url = 'https://plus.google.com/share?url={}'.format(link)
    return url


@register.filter
def reddit_share(request, article):
    """
    Given a request, an article, it returns a reddit share url.
    """
    link, title = _get_url_title(request, article)
    url = 'https://www.reddit.com/submit?url={}&title={}'.format(link, title)
    return url


@register.filter
def pinterest_share(request, article):
    """
    Given a request, an article, it returns a pinterest share url.
    """
    link, title = _get_url_title(request, article)
    if article.primary_media:
        if hasattr(article.primary_media, 'is_video'):
            image = article.primary_media.link
        else:
            image = article.primary_media.image_sm.url
    else:
        try:
            image = staticfiles_storage.url('img/logos/sf-logo-x256.png')
        except ValueError:  # no access to cdn at this time
            image = ''
    url = 'https://pinterest.com/pin/create/button/?url={}&description={}&media={}'.format(link, title, image)
    return url


@register.filter
def linkedin_share(request, article):
    """
    Given a request, an article, it returns a linkedin share url.
    """
    site_name = getattr(settings, 'SITE_NAME', '')
    link, title = _get_url_title(request, article)
    url = 'https://www.linkedin.com/shareArticle?mini=true&url={}&title={}&source={}'.format(link, title, site_name)
    return url


@register.filter
def email_share(request, article):
    """
    Given a request, an article, it returns an email share url.
    """
    url, title = _get_url_title(request, article)
    return url
