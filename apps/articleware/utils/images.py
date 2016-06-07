from toolware.utils.generic import get_uuid

from .common import image_path_year_month_size


def uploadto_image_to_year_month(instance, filename):
    return image_path_year_month_size(filename,
        prefix='images/cache', size='')


def uploadto_image_to_year_month_sm(instance, filename):
    return image_path_year_month_size(filename,
        prefix='images/cache', size='sm')


def uploadto_image_to_year_month_md(instance, filename):
    return image_path_year_month_size(filename,
        prefix='images/cache', size='md')


def uploadto_image_to_year_month_lg(instance, filename):
    return image_path_year_month_size(filename,
        prefix='images/cache', size='lg')


def uploadto_image_to_year_month_xl(instance, filename):
    return image_path_year_month_size(filename,
        prefix='images/cache', size='xl')


def uploadto_image_to_year_month_uuid(instance, filename):
    unique_id = get_uuid(12, 4)
    return image_path_year_month_size(filename,
        prefix='images/cache', size='', unique_id=unique_id)


def uploadto_image_to_year_month_uuid_sm(instance, filename):
    unique_id = get_uuid(12, 4)
    return image_path_year_month_size(filename,
        prefix='images/cache', size='sm', unique_id=unique_id)


def uploadto_image_to_year_month_uuid_md(instance, filename):
    unique_id = get_uuid(12, 4)
    return image_path_year_month_size(filename,
        prefix='images/cache', size='md', unique_id=unique_id)


def uploadto_image_to_year_month_uuid_lg(instance, filename):
    unique_id = get_uuid(12, 4)
    return image_path_year_month_size(filename,
        prefix='images/cache', size='lg', unique_id=unique_id)


def uploadto_image_to_year_month_uuid_xl(instance, filename):
    unique_id = get_uuid(12, 4)
    return image_path_year_month_size(filename,
        prefix='images/cache', size='xl', unique_id=unique_id)
