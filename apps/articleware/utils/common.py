import os
import hmac
from hashlib import sha1

from django.conf import settings
from django.utils.timezone import now
from django.core.urlresolvers import reverse

from bs4 import BeautifulSoup
from slugify import slugify
from toolware.compat import unescape
from toolware.compat import urlparse
from toolware.compat import quote
from toolware.utils.generic import get_uuid

from .. import defaults as defs


def get_template_path(name):
    """
    Given a template name, it returns the relative path from the template dir.
    """
    path = os.path.join(defs.ARTICLEWARE_TEMPLATE_BASE_DIR, name)
    return path


def get_url_salted_hash(url):
    """
    Returns a signature for url
    """
    clean_char_list = {
        ' ': '%20',
        '+': '%20',
    }
    for cha in clean_char_list:
        url = url.replace(cha, clean_char_list[cha])

    salt = settings.SECRET_KEY
    encoded = '{}{}'.format(quote(url, safe="%/:=&?~#+!$,;'@()*[] "), salt).encode()
    seekret = hmac.new(encoded, digestmod=sha1).hexdigest()
    return seekret


def securify_external_links(html, is_secure=False):
    """
    Given a html snippet, it returns a version where all external http URLs go through secure redirect.
    """
    soup = BeautifulSoup(unescape(html))
    for tag in soup.find_all(True):
        if tag.name.lower() == 'a':
            old_href = tag['href'].strip().lower()
            if is_secure and 'http' in old_href and 'https' not in old_href:
                domain = urlparse.urlparse(old_href).hostname
                redirector = reverse('articleware:article_securify_url_view')
                signutre = get_url_salted_hash(old_href)
                new_href = '{}?goto={}&url={}&sig={}'.format(redirector, domain, old_href, signutre)
                tag['href'] = new_href
            if 'http' in old_href:
                tag['rel'] = 'nofollow'
                tag['target'] = '_blank'
    cleaned = soup.renderContents()
    return cleaned


def strip_all_tags(html, disallowed_tags=defs.ARTICLEWARE_DISALLOWED_TAGS):
    """
    Given a html snippet, returns  a cleaned version with all disallowed tags removed.
    """
    cleaned = ''
    if html:
        soup = BeautifulSoup(unescape(html))
        for tag in soup.find_all(True):
            if tag.name in disallowed_tags:
                tag.extract()
            else:
                tag.hidden = True
        cleaned = soup.renderContents()
    return cleaned


def clean_linebreaks(html):
    """
    Given an unescape html, it will return a cleaned html with all leading/trailing linebreaks removed.
    This is specific for when <p><br></p> is used as linebreaks and it assumes that <br/> is removed by
    the calling functions so <p></p> is our linebreaks. It also enforces max consecutive linebreaks as per
    settings. When done, it will re-insert <br/> into the remaining empty <p></p> to form <p><br/></p>
    to satisfy the wysiwyg editor.  The template rendering can choose to replace <p><br/></p> with just <br>.
    """
    cleaned = ''
    if html:
        seen_real_content_yet = False
        consecutive_linebreaks = []
        soup = BeautifulSoup(html)

        for tag in soup.find_all(True):
            if tag.name == 'p':
                if tag.contents:
                    seen_real_content_yet = True
                    consecutive_linebreaks = []
                else:
                    if not seen_real_content_yet:
                        tag.extract()
                    else:
                        if len(consecutive_linebreaks) < defs.ARTICLEWARE_MAX_CONSECUTIVE_LINEBREAKS:
                            tag.contents.append(soup.new_tag('br'))
                            consecutive_linebreaks.append(tag)
                        else:
                            tag.extract()
            else:
                seen_real_content_yet = True
                consecutive_linebreaks = []

        for tag in consecutive_linebreaks:
            tag.extract()

        cleaned = soup.renderContents()
    return cleaned


def process_tag(tag, allowed_tags, disallowed_tags):
    """
    Given a tag, it will flatten it if not allowed and remove it if disallowed.
    """
    if tag.name not in allowed_tags:
        tag.hidden = True
    if tag.name in disallowed_tags:
        tag.extract()
    return tag


def get_sanitized_html(html, allowed_tags=defs.ARTICLEWARE_ALLOWED_TAGS,
    disallowed_tags=defs.ARTICLEWARE_DISALLOWED_TAGS):
    """
    Given a html snippet, returns  a cleaned version with all disallowed tags removed.
    """
    cleaned = ''
    if html:
        soup = BeautifulSoup(unescape(html))
        for tag in soup.find_all(True):
            process_tag(tag, allowed_tags, disallowed_tags)
        cleaned = soup.renderContents()
    return clean_linebreaks(cleaned)


def sanitization_required(html, allowed_tags=defs.ARTICLEWARE_ALLOWED_TAGS):
    """
    Return True, if it find a disallowed tags, or returns False.
    """
    if not html:
        return False
    html = html.replace('&nbsp;', '')
    soup = BeautifulSoup(unescape(html))
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags + ['br']:
            return True
    return False


def is_sanitized_html_blank(html):
    """
    Return True, if after cleanup there is no content, or False
    """
    if not html:
        return True

    disallowed_tags = defs.ARTICLEWARE_DISALLOWED_TAGS
    allowed_tags = defs.ARTICLEWARE_ALLOWED_TAGS

    soup = BeautifulSoup(unescape(html))
    for tag in soup.find_all(True):
        process_tag(tag, allowed_tags, disallowed_tags)
    cleaned = soup.renderContents().strip()
    if cleaned:
        return False

    return True


def image_path_to_year_month(filename):
    """
    Given an image instance, returns a relative path for the image.
    """
    base, ext = os.path.splitext(filename.lower())
    date = now().strftime("%Y/%m/%d")
    upload_to = 'images/{}/{}{}'.format(date, slugify(base), ext)
    return upload_to


def image_path_year_month_size(filename, prefix='', size='', unique_id=''):
    """
    Given an image filename, returns a relative path to the image.
    """
    if size is None:
        raise FileSizeNotIsMissing

    if prefix:
        prefix = '{}/'.format(prefix)

    if unique_id:
        unique_id = '_{}'.format(unique_id)

    if size:
        size = '_{}'.format(size)

    base, ext = os.path.splitext(filename.lower())
    date = now().strftime("%Y/%m/%d")

    upload_to = '{}images/{}/{}{}{}{}'.format(prefix, date, slugify(base, separator='_'), unique_id, size, ext)
    return upload_to


def is_article_admin(request):
    if request.user.groups.filter(name=defs.ARTICLEWARE_GROUP_ARTICLE_ADMIN['admin']).exists():
        return True
    elif request.user.is_superuser:
        return True
    return False


def is_article_tags_admin(request):
    if is_article_admin(request):
        return True
    elif request.user.groups.filter(name=defs.ARTICLEWARE_GROUP_ARTICLE_ADMIN['tags']).exists():
        return True
    return False


def is_article_targets_admin(request):
    if is_article_admin(request):
        return True
    elif request.user.groups.filter(name=defs.ARTICLEWARE_GROUP_ARTICLE_ADMIN['targets']).exists():
        return True
    return False


def is_article_categories_admin(request):
    if is_article_admin(request):
        return True
    elif request.user.groups.filter(name=defs.ARTICLEWARE_GROUP_ARTICLE_ADMIN['categories']).exists():
        return True
    return False


def is_article_blog_admin(request):
    if request.user.groups.filter(name=defs.ARTICLEWARE_GROUP_ARTICLE_ADMIN['blog']).exists():
        return True
    elif request.user.is_superuser:
        return True
    return False


def is_article_page_admin(request):
    if request.user.groups.filter(name=defs.ARTICLEWARE_GROUP_ARTICLE_ADMIN['page']).exists():
        return True
    elif request.user.is_superuser:
        return True
    return False


def get_approved_writer_group_name():
    return defs.ARTICLEWARE_GROUP_ARTICLE_ADMIN['writer']


def is_approved_writer(request):
    if request.user.groups.filter(name=get_approved_writer_group_name()).exists():
        return True
    elif request.user.is_superuser:
        return True
    return False


def is_article_action_authorized(request, type):
    if not defs.ARTICLEWARE_GROUP_ARTICLE_ADMIN_ENFORCE_PERMISSIONS.get(type, False):
        return True
    if is_article_admin(request):
        return True
    action = defs.ARTICLEWARE_GROUP_ARTICLE_ADMIN.get(type, None)
    if action:
        if request.user.groups.filter(name=action).exists():
            return True
    return False


def get_article_public_short_url(request, article):
    get_absolute_short_url = reverse('articleware:article_short_url_view', kwargs={'uuid': article.uuid})
    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()
    url = '{}://{}{}'.format(protocol, domain, get_absolute_short_url)
    return url
