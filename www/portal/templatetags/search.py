import six

from django import template
from django.http import QueryDict
from django.contrib.auth import get_user_model

from .. import utils as util

register = template.Library()
User = get_user_model()


@register.assignment_tag(takes_context=True)
def category_search_info(context, category, path='search'):
    """
    Given a category, it returns the URL for add/removing the category from search filter.
    """
    name = category.slug
    info_dict = util.get_object_filter_info(context, name, 'category', path)
    return info_dict


@register.assignment_tag(takes_context=True)
def tag_search_info(context, tag, path='search'):
    """
    Given a tag, it returns the URL for add/removing the tag from search filter.
    """
    name = tag.slug
    info_dict = util.get_object_filter_info(context, name, 'tag', path)
    return info_dict


@register.assignment_tag(takes_context=True)
def author_search_info(context, author, path='search'):
    """
    Given a author (User) or string (username), it returns the URL for add/removing the user from search filter.
    """
    if not isinstance(author, six.string_types):
        name = author.username
    else:
        name = author
    info_dict = util.get_object_filter_info(context, name, 'author', path)
    return info_dict


@register.assignment_tag(takes_context=True)
def pagination_url(context, next_page, path='search'):
    """
    Given a path, it returns the URL for the next page.
    """
    query_dict = context['request'].GET.copy()
    if 'history' in query_dict:
        del query_dict['history']
    query_dict.setlist('page', [next_page])
    return util.get_filter_absolute_url(query_dict, path)


@register.assignment_tag(takes_context=True)
def current_params(context, type, path='search'):
    """
    Given a context, returns the current params for the type.
    Example: type = `category`, `tags`, `targets` etc.
    """
    info_dict = util.get_type_filter_info_dict(context, type, path)
    return info_dict


@register.assignment_tag(takes_context=True)
def get_author(context, username, path='search'):
    """
    Given a username, it returns an user object or None
    """
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


@register.assignment_tag(takes_context=True)
def get_title_info(context):
    """
    It returns a string usable in title.
    """
    query_dict = context['request'].GET.copy()
    exclude = ['history', 'page', 'author']
    for item in exclude:
        if item in query_dict:
            del query_dict[item]

    final_list = []
    for param in query_dict:
        for item in query_dict.getlist(param):
            if item not in final_list:
                final_list.append(item)
    return ' '.join(final_list)


@register.filter
def pub_long_link(request, article):
    """
    Given a request and an article, it returns the fully qualified long public URL.
    """
    url = util.get_article_public_long_url(request, article)
    return url


@register.assignment_tag(takes_context=True)
def get_related(context, article, count):
    """
    Given an article, it returns `count` number of related objects
    """
    related = article.related(count)
    return related
