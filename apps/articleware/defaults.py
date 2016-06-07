from django.conf import settings
from django.utils.translation import ugettext

from pilkit import processors
from toolware.utils.country import COUNTRIES

ARTICLEWARE_MAX_IMAGE_SIZE = 15  # MB
ARTICLEWARE_VALID_IMAGE_FORMATS = ('image/png', 'image/jpeg', 'image/gif', 'image/jpg')
ARTICLEWARE_CONNECTION_REQUEST_TIMEOUT = 6  # Seconds. When making url request
ARTICLEWARE_REFERER = getattr(settings, 'SITE_DOMAIN', 'Example.com')
ARTICLEWARE_ASSET_VERSION = getattr(settings, 'MANIFEST_STATIC_FILE_VERSION', '0.0.6')
ARTICLEWARE_YOUTUBE_LINK_FORMAT = 'https://www.youtube.com/watch?v='
ARTICLEWARE_MAX_CATEGORIES_PER_ARTICLE = 2
ARTICLEWARE_MAX_TARGETS_PER_ARTICLE = 3
ARTICLEWARE_MAX_TAGS_PER_ARTICLE = 4

ARTICLEWARE_ACTIVITY_CACHE = 40  # seconds
ARTICLEWARE_ACTIVE_CATEGORY_CACHE = 60 * 5  # 5 minutes
ARTICLEWARE_ARTICLE_HIT_CACHE_TIMEOUT_MINUTES = 259200  # 3 days
ARTICLEWARE_ARTICLE_VIEW_CACHE_TIMEOUT_MINUTES = 259200  # 3 days

ARTICLEWARE_VIDEO_PROVIDERS = {
    'youtube': {
        'name': 'youtube',
        'domain': ['youtube.com', 'youtu.be'],
        'video_link': 'https://www.youtube.com/embed/{}',
        'thumbnail_link': 'https://i.ytimg.com/vi/{}/{}.jpg',
        'thumb_quality': ['maxresdefault', 'hqdefault', 'sddefault', 'default', '0', '1', '2', '3'],
    },
    'vimeo': {
        'name': 'vimeo',
        'domain': ['vimeo.com', 'i.vimeocdn.com'],
        'video_link': 'https://player.vimeo.com/video/{}',
        'thumbnail_link': 'https://vimeo.com/api/v2/video/{}.json',
        'thumb_quality': ['thumbnail_large', 'thumbnail_medium', 'thumbnail_small'],
    }
}

ARTICLEWARE_MAX_CONSECUTIVE_LINEBREAKS = 1
ARTICLEWARE_TABLE_TAGS = ['table', 'tbody', 'tr', 'td', ]
ARTICLEWARE_ALLOWED_TAGS = ['a', 'b', 'i', 'u', 'strike', 'strong', 'em', 'p'] + ARTICLEWARE_TABLE_TAGS
ARTICLEWARE_DISALLOWED_TAGS = ['script', 'embed', 'video']

ARTICLEWARE_MAX_SNIPPETS_PER_ARTICLE = 30
ARTICLEWARE_MAX_IMAGES_PER_SNIPPET = 10
ARTICLEWARE_MAX_VIDEOS_PER_SNIPPET = 10

ARTICLEWARE_REMOVE_IMAGE_CACHE_ON_DELETION = getattr(settings, 'ARTICLEWARE_REMOVE_IMAGE_CACHE_ON_DELETION', False)

ARTICLEWARE_STORAGE_CLASS = getattr(settings, 'ARTICLEWARE_STORAGE_CLASS', getattr(
    settings, 'DEFAULT_FILE_STORAGE'))

ARTICLEWARE_TEMPLATE_BASE_DIR = getattr(settings, 'ARTICLEWARE_TEMPLATE_BASE_DIR', 'article')

ARTICLEWARE_RESOLUTIONS = {
    'enabled': {
        'xs': {
            'size': 'extra small',
            'quality': 70,
            'width': 200,
            'height': 113,
            'format': 'JPEG',
        },
        'sm': {
            'size': 'small',
            'quality': 80,
            'width': 480,
            'height': 270,
            'format': 'JPEG',
        },
        'md': {
            'size': 'medium',
            'tag': 'md',
            'quality': 85,
            'width': 961,
            'height': 540,
            'format': 'JPEG',
        },
        'lg': {
            'size': 'large',
            'tag': 'lg',
            'quality': 90,
            'width': 1280,
            'height': 720,
            'format': 'JPEG',
        },
        'xl': {
            'size': 'extra large',
            'tag': 'xl',
            'quality': 95,
            'width': 1600,
            'height': 900,
            'format': 'JPEG',
        },
        'sl': {
            'size': 'super large',
            'tag': 'xl',
            'quality': 100,
            'width': 1920,
            'height': 1080,
            'format': 'JPEG',
        },
    }
}

ARTICLEWARE_INITIAL_CATEGORIES = [
    'Arts',
    'Beauty & Style',
    'Business',
    'Finance',
    'Economy',
    'Cars & Automotive',
    'Transportation',
    'Computers',
    'Internet',
    'Consumer Electronics',
    'Green Tech',
    'Technology',
    'Dining Out',
    'Education',
    'Entertainment',
    'Music',
    'Environment',
    'Sustainability',
    'Family',
    'Relationships',
    'Food',
    'Drink',
    'Games',
    'Recreation',
    'Health',
    'Fitness',
    'Home & Garden',
    'Local Businesses',
    'News & Events',
    'Pets',
    'Politics',
    'Governments',
    'Pregnancy',
    'Parenting',
    'Science',
    'Mathematics',
    'Social Science',
    'Social Media',
    'Society & Cultures',
    'Beliefs',
    'Sports',
    'Travel',
    'Hobbies',
    'Celebrities',
    'Geography',
    'Entrepreneurship',
    'What-If',
    'Ideas',
    'History',
    'Nature',
    'Marketing',
    'Lifestyle',
    'Laws',
    'Photography',
    'Philosophy',
    'Movies',
    'Real Estates',
]

ARTICLEWARE_INITIAL_TAGS = [
    'Apple',
    'Amazon',
    'Google',
    'Microsoft',
    'Twitter',
    'News',
    'Food',
    'Cars',
    'Funny',
    'Movie',
    'Music',
    'Technology',
    'Geography',
    'History',
    'Marketing',
    'Social Media',
    'Social Networking',
    'Entrepreneurship',
    'Green Tech',
    'Entertainment',
    'Environment',
]

ARTICLEWARE_INITIAL_TARGETING_TAGS = [ugettext(x[1]) for x in COUNTRIES]

ARTICLEWARE_ACTIVE_IMAGE_PROCESSORS = [
    'ResizeToFill',
    'ResizeToFit',
    'ResizeCanvas',
    # 'ResizeToCover',
    # 'SmartResize',
    # 'Thumbnail',
    # 'Resize',
]

ARTICLEWARE_AVAILABLE_IMAGE_PROCESSORS = {
    'ResizeToFill': processors.ResizeToFill,
    'ResizeToFit': processors.ResizeToFit,
    'ResizeCanvas': processors.ResizeCanvas,
    'ResizeToCover': processors.ResizeToCover,
    'SmartResize': processors.SmartResize,
    'Thumbnail': processors.Thumbnail,
    'Resize': processors.Resize,
}

ARTICLEWARE_GROUP_ARTICLE_ADMIN = {
    'admin': 'article:admin:all',
    'tags': 'article:admin:tags',
    'targets': 'article:admin:targets',
    'categories': 'article:admin:categories',
    'blog': 'article:admin:blog',
    'writer': 'article:admin:writer',
    'page': 'article:admin:page',
}

ARTICLEWARE_GROUP_ARTICLE_ADMIN_ENFORCE_PERMISSIONS = {
    'tags': False,
    'targets': True,
    'categories': True,
}
