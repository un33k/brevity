import os
import re
import json
import requests

from toolware.utils.generic import get_url_args

from .. import defaults as defs


def get_video_provider_by_url(url):
    for provider in defs.ARTICLEWARE_VIDEO_PROVIDERS:
        for domain in defs.ARTICLEWARE_VIDEO_PROVIDERS[provider]['domain']:
            if domain.lower() in url.lower():
                return defs.ARTICLEWARE_VIDEO_PROVIDERS[provider]
    return None


def get_video_provider_by_name(name):
    for provider in defs.ARTICLEWARE_VIDEO_PROVIDERS:
        if provider.lower() in name.lower():
                return defs.ARTICLEWARE_VIDEO_PROVIDERS[provider]
    return None


def get_video_info(url):
    found = False
    info = {
        'vid': None,
        'msg': 'Unsupported provider.',
    }
    provider = get_video_provider_by_url(url)
    if provider:
        if 'youtube' in provider['name']:
            vid, link, thumb = get_youtube_info(url)
        elif 'vimeo' in provider['name']:
            vid, link, thumb = get_vimeo_info(url)
        if link and vid and thumb:
            base, ext = os.path.splitext(os.path.basename(thumb))
            info['name'] = provider['name']
            info['vid'] = vid
            info['filename'] = vid + ext
            info['link'] = link
            info['thumb'] = thumb
            info['msg'] = '{} Video.'.format(provider['name'].capitalize())
            found = True
        else:
            info['msg'] = 'Unavailable video or bad link.'
    return found, info


def get_youtube_info(url):
    vid, link, thumb = None, None, None
    provider = get_video_provider_by_name('youtube')
    vid_pattern = '((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)'
    matched = re.search(vid_pattern, url)
    if matched:
        vid = matched.group(4)
        link = provider['video_link'].format(vid)
        thumb = get_youtube_best_thumbnail_quality(vid)
    return vid, link, thumb


def get_youtube_best_thumbnail_quality(vid):
    provider = get_video_provider_by_name('youtube')
    for quality in provider['thumb_quality']:
        thumb_link = provider['thumbnail_link'].format(vid, quality)
        resp = requests.head(thumb_link)
        if resp.status_code == 200:
            return thumb_link
    return None


def get_vimeo_info(url):
    vid, link, thumb = None, None, None
    provider = get_video_provider_by_name('vimeo')
    vid_pattern = '(https?://)?(www.)?(player.)?(i.)?vimeo.com/([a-z]*/)*([0-9]{6,11})[?]?.*'
    matched = re.search(vid_pattern, url)
    if matched:
        vid = matched.group(6)
        link = provider['video_link'].format(vid)
        thumb = get_vimeo_best_thumbnail_quality(vid)
    return vid, link, thumb


def get_vimeo_best_thumbnail_quality(vid):
    provider = get_video_provider_by_name('vimeo')
    thumbnail_info_link = provider['thumbnail_link'].format(vid)
    resp = requests.get(thumbnail_info_link)
    if resp.status_code != 200:
        return None

    for info in list(resp.json()):
        for quality in provider['thumb_quality']:
            thumb_link = info.get(quality)
            if thumb_link:
                resp = requests.head(thumb_link)
                if resp.status_code == 200:
                    return thumb_link
    return None
