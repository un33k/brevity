import os

from rest_framework.reverse import reverse

from . import defaults as defs


def get_template_path(name):
    """
    Given a template name, it returns the relative path from the template dir.
    """
    path = os.path.join(defs.PORTAL_TEMPLATE_BASE_DIR, name)
    return path


def get_object_filter_info(context, item_name, item_type, path):
    query_dict = context['request'].GET.copy()
    if 'page' in query_dict:
        del query_dict['page']
    if 'history' in query_dict:
        del query_dict['history']

    is_selected = False
    if item_type in query_dict:
        current_list = query_dict.getlist(item_type)
        if item_name in current_list:
            is_selected = True
            current_list.remove(item_name)
        else:
            current_list.append(item_name)
        new_list = current_list
    else:
        new_list = [item_name]

    query_dict.setlist(item_type, new_list)

    info_dict = {
        'is_selected': is_selected,
        'url': get_filter_absolute_url(query_dict, path),
    }
    return info_dict


def get_type_filter_info_dict(context, type, path):
    query_dict = context['request'].GET.copy()
    if 'page' in query_dict:
        del query_dict['page']
    if 'history' in query_dict:
        del query_dict['history']

    info_dict = {}
    if type in query_dict:
        current_list = list(query_dict.getlist(type))
        for item in current_list:
            work_list = list(current_list)
            work_list.remove(item)
            query_dict.setlist(type, work_list)
            info_dict[item] = get_filter_absolute_url(query_dict, path)
    return info_dict


def get_filter_absolute_url(query_dict, path):
    encoded_params = query_dict.urlencode()
    restore_chars = {
        '%2C': ',',
        '%2c': ',',
    }
    for char in restore_chars:
        encoded_params = encoded_params.replace(char, restore_chars[char])
    url = '/{}?{}'.format(path, encoded_params)
    return url


def get_article_public_long_url(request, article):
    get_absolute_long_url = reverse('portal:article_view', kwargs={'uuid': article.uuid, 'slug': article.slug})
    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()
    url = '{}://{}{}'.format(protocol, domain, get_absolute_long_url)
    return url
