import os
import datetime

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core import validators
from django.utils.translation import gettext as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.template.defaultfilters import timesince_filter
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.humanize.templatetags.humanize import naturalday

from taggit.managers import TaggableManager

from toolware.utils.query import CaseInsensitiveManager
from toolware.utils.generic import get_uuid

from slugify import slugify

from .tags import ContentTaggedItem
from .tags import CategoryTaggedItem
from .tags import TargetingTaggedItem
from .track import Track
from .. import utils as util
from .. import defaults as defs


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


def article_uuid(length=12):
    """
    Get a 12 digit long uuid for articles.
    """
    count = 0
    while(count < 5):
        uuid = get_uuid(length, 4)
        try:
            Article.objects.get(uuid=uuid)
        except Article.DoesNotExist:
            return uuid
        count += 1
    return get_uuid(length, 4)


@python_2_unicode_compatible
class Article(models.Model):
    """
    Article of all kinds. Blog, Review, Event etc.
    """
    ARTICLE_STATUS_PUBLIC = 'Public'
    ARTICLE_STATUS_UNLISTED = 'Unlisted'
    ARTICLE_STATUS_PRIVATE = 'Private'
    ARTICLE_STATUS_ARCHIVED = 'Archived'
    ARTICLE_STATUS_CHOICES = (
        (ARTICLE_STATUS_PUBLIC, ARTICLE_STATUS_PUBLIC),
        (ARTICLE_STATUS_UNLISTED, ARTICLE_STATUS_UNLISTED),
        (ARTICLE_STATUS_PRIVATE, ARTICLE_STATUS_PRIVATE),
        (ARTICLE_STATUS_ARCHIVED, ARTICLE_STATUS_ARCHIVED),
    )

    ARTICLE_FLAVOR_ARTICLE = 'Article'
    ARTICLE_FLAVOR_BLOG = 'Blog'
    ARTICLE_FLAVOR_PAGE = 'Page'
    ARTICLE_FLAVOR_CHOICES = (
        (ARTICLE_FLAVOR_ARTICLE, ARTICLE_FLAVOR_ARTICLE),
        (ARTICLE_FLAVOR_BLOG, ARTICLE_FLAVOR_BLOG),
        (ARTICLE_FLAVOR_PAGE, ARTICLE_FLAVOR_PAGE),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    uuid = models.CharField(
        max_length=12,
        default=article_uuid,
        editable=False,
    )

    author = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="author",
        blank=True,
        null=True,
        help_text=_("Author of this post."),
    )

    editor = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="editor",
        blank=True,
        null=True,
        help_text=_("Last editor of this post."),
    )

    flavor = models.CharField(
        _("Flavor"),
        max_length=20,
        choices=ARTICLE_FLAVOR_CHOICES,
        default=ARTICLE_FLAVOR_ARTICLE,
        help_text=_("Article type. (Ex: Article, Blog, Page)."),
    )

    status = models.CharField(
        _("Visibility"),
        max_length=20,
        choices=ARTICLE_STATUS_CHOICES,
        default=ARTICLE_STATUS_UNLISTED,
        help_text=_("Visibility. Public=ByAll, Unlisted=ByLink, Private=ByNobody, Archived=Private+Historical."),
    )

    headline = models.TextField(
        _("Headline"),
        blank=False,
        validators=[validators.MinLengthValidator(10), validators.MaxLengthValidator(120)],
        help_text=_("Headline for this post."),
    )

    description = models.TextField(
        _("Description"),
        blank=True,
        null=True,
        validators=[validators.MinLengthValidator(15), validators.MaxLengthValidator(255)],
        help_text=_("Short description for this post."),
    )

    slug = models.CharField(
        _("Slug"),
        max_length=120,
        blank=False,
        editable=False,
        help_text=_("Cleaned up version of the title to be used in the URL."),
    )

    categories = TaggableManager(
        related_name="categories",
        through=CategoryTaggedItem,
        verbose_name=_("Categories"),
        blank=True,
        help_text=_("Comma-separated categories. (Ex: Technology, Finance etc.)"),
    )

    tags = TaggableManager(
        related_name="tags",
        through=ContentTaggedItem,
        verbose_name=_("Tags"),
        blank=True,
        help_text=_("Comma-separated tags. (Ex: Android, iPhone, Life, Travel etc.)"),
    )

    featured = models.BooleanField(
        _("Featured"),
        default=False,
        help_text=_("If this is a featured article."),
    )

    # ########## Add new fields above this line #############
    objects = CaseInsensitiveManager()

    CASE_INSENSITIVE_FIELDS = ['type', 'headline', ]

    class Meta:
        unique_together = (("author", "headline", "flavor"),)

    def __str__(self):
        name = ''
        if self.id:
            name = u'{} [{}]'.format(self.author, self.headline[:40])
        return name

    def is_author(self, user):
        author = self.author == user
        return author

    def is_editor(self, user):
        editor = self.editor == user
        return editor

    @property
    def likes(self):
        likes = self.track.like
        return likes

    @property
    def has_approved_author(self):
        approved = self.author.groups.filter(name=util.get_approved_writer_group_name()).exists()
        return approved

    @property
    def primary_video(self):
        """
        Returns the first match video object or None.
        """
        snippets = self.snippets.filter(type=self.snippet.model.SNIPPET_TYPE_VIDEO)
        for snippet in snippets:
            for video in snippet.videos:
                if video.vid and video.image:
                    return video
        return None

    @property
    def primary_image(self):
        """
        Returns the first match image object or None.
        """
        snippets = self.snippets.filter(type=self.snippet.model.SNIPPET_TYPE_IMAGE)
        for snippet in snippets:
            for image in snippet.images:
                if image.image.url:
                    return image
        return None

    @property
    def primary_media(self):
        """
        Returns the first match image/video object or None.
        """
        snippets = self.snippets \
            .filter(~Q(type=self.snippet.model.SNIPPET_TYPE_TEXT)) \
            .order_by('priority')

        for snippet in snippets:
            if snippet.type == self.snippet.model.SNIPPET_TYPE_VIDEO:
                for video in snippet.videos:
                    if video.vid and video.image:
                        return video
            elif snippet.type == self.snippet.model.SNIPPET_TYPE_IMAGE:
                for image in snippet.images:
                    if image.image.url:
                        return image
        return None

    @property
    def primary_content(self):
        """
        Returns the first match text object or None.
        """
        snippets = self.snippets.filter(type=self.snippet.model.SNIPPET_TYPE_TEXT)
        for snippet in snippets:
            if snippet.content:
                return snippet.content
        return None

    @property
    def primary_category(self):
        """
        Returns the first category for article when one or multiple categories are present.
        """
        category = self.categories.all().first()
        return category

    @property
    def unique_tags(self):
        """
        Tags that have not appeared also in categories.
        """
        categories = [a.lower() for a in self.categories.values_list('name', flat=True)]

        tags = self.tags.all()
        unique_tags = []
        for tag in tags:
            if tag.name.lower() not in categories:
                unique_tags.append(tag)
        return unique_tags

    @property
    def snippets(self):
        """
        Returns the first match image object or None.
        """
        snippets = self.snippet.all().order_by('priority', '-created_at')
        return snippets

    @property
    def has_warning(self):
        """
        Returns True if article has warnings.
        Ex: Empty snippets etc.
        """
        if not self.primary_content:
            return True
        for snippet in self.snippets:
            if not snippet.is_ready:
                return True
        return False

    @property
    def is_public(self):
        public = self.status == self.ARTICLE_STATUS_PUBLIC
        return public

    @property
    def is_unlisted(self):
        public = self.status == self.ARTICLE_STATUS_UNLISTED
        return public

    @property
    def is_private(self):
        public = self.status == self.ARTICLE_STATUS_PRIVATE
        return public

    @property
    def is_archived(self):
        archived = self.status == self.ARTICLE_STATUS_ARCHIVED
        return archived

    @property
    def is_blog(self):
        blog = self.flavor == self.ARTICLE_FLAVOR_BLOG
        return blog

    @property
    def is_page(self):
        page = self.flavor == self.ARTICLE_FLAVOR_PAGE
        return page

    def _event_time(self, event_time):
        """
        Returns creation time to produce:
        1-59 second = just now
        1-59 minutes = x minutes ago
        1-23 hours = x hours ago
        1-30 days = x days ago
        1-12 months = x months ago
        1-X years = actual date
        """
        happend = event_time
        now = timezone.now()
        delta = now - happend

        if delta.days < 1 and delta.seconds < 60:
            # 0 - 59 second(s) is now
            return naturaltime(happend.replace(second=0))
        elif delta.days < 1 and delta.seconds // 60 < 60:
            # 1 - 59 minute(s) without seconds
            return naturaltime(happend.replace(second=0))
        elif delta.days < 1 and delta.seconds // 60 // 60 < 24:
            # 1 - 23 hour(s) without minutes or seconds
            happend = happend.replace(minute=0, second=0)
            return naturaltime(happend.replace(minute=0, second=0))
        return ''

    @property
    def creation_time(self):
        return self._event_time(self.created_at)

    @property
    def publication_time(self):
        return self._event_time(self.published_at)

    @property
    def update_time(self):
        return self._event_time(self.updated_at)

    def related(self, count=10):
        """
        Returns list of related article based on tags.
        """
        q_list = Q(categories__in=self.categories.all()) | Q(tags__in=self.tags.all())
        if self.targets.count():
            q_list &= Q(targets__in=self.targets.all())

        approved_group = util.get_approved_writer_group_name()
        approved_query = Q(author__groups__name=approved_group)

        related = Article.objects \
            .filter(q_list) \
            .filter(approved_query) \
            .filter(status=self.ARTICLE_STATUS_PUBLIC) \
            .filter(flavor=self.flavor) \
            .exclude(id=self.id) \
            .exclude(author__is_active=False) \
            .distinct() \
            .order_by('-published_at')[:4]
        return related

    def get_absolute_url(self):
        """
        Returns public URL for this post
        """
        return "/article/{}/{}".format(self.uuid, self.slug)

    def get_absolute_url_short(self):
        """
        Returns shorten public URL for this post
        """
        return "/article/{}".format(self.uuid)

    def get_page_absolute_url(self):
        """
        Returns public URL for this post
        """
        return "/site/{}".format(self.slug)

    def _set_publish_time(self):
        """
        Captures the publish time.
        """
        if self.is_public and not self.published_at:
            self.published_at = timezone.now()

    def save(self, *args, **kwargs):
        if self.headline:
            self.slug = slugify(self.headline)
        self.editor = self.editor or self.author
        self._set_publish_time()
        super(Article, self).save(*args, **kwargs)

# Create a track object on demand if not already created
Article.track = property(lambda self: Track.objects.get_or_create(article=self)[0])
