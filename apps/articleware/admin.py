from django.conf import settings
from django.db import models
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from taggit.models import Tag

from .models import Article
from .models import Track
from .models import Snippet
from .models import Image
from .models import Video
from .models import ContentTag
from .models import ContentTaggedItem
from .models import CategoryTag
from .models import CategoryTaggedItem
from .models import TargetingTag
from .models import TargetingTaggedItem

from .forms import ImageForm
from .forms import VideoForm
from .forms import SnippetTextForm
from .forms import SnippetImageForm
from .forms import SnippetVideoForm

from . import utils as util


class AdminImageWidget(forms.FileInput):
    """A FileField Widget that shows CDN file link"""
    def __init__(self, attrs={}):
        super(AdminImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, 'url'):
            tmpl = '<a href="{0}" target="_blank"><img src="{0}" width=120 height=68/></a><br/>{1} {2}<br />{3}'
            output.append(tmpl.format(value.url, 'Link: ', value.url, 'Change: '))
        output.append(super(AdminImageWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class ImageForm(forms.ModelForm):
    """
    Image Admin Form
    """
    class Meta:
        model = Image
        fields = '__all__'
        widgets = {
            'image': AdminImageWidget,
        }


class ImageInline(admin.TabularInline):
    model = Image
    form = ImageForm
    extra = 0


class ImageAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'thumb',
        'priority',
        'snippet',
        'image',
    )
    readonly_fields = ['thumb']
    search_fields = [
        'snippet__id',
    ]
admin.site.register(Image, ImageAdmin)


class VideoInline(admin.TabularInline):
    model = Video
    form = VideoForm
    extra = 0


class VideoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'thumb',
        'priority',
        'snippet',
        'vid',
        'provider'
    )
    readonly_fields = ['thumb']
    search_fields = [
        'snippet__id',
    ]
admin.site.register(Video, VideoAdmin)


class SnippetAdmin(admin.ModelAdmin):

    inlines = [ImageInline, VideoInline, ]

    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size': 120})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 30, 'cols': 120})},
    }

    list_display = (
        'id',
        'article',
        'type',
        'priority',
        'caption',
        'content',
        'updated_at',
        'created_at',
    )

    search_fields = [
        'id',
        'type',
        'author__email',
        'editor__email',
        'priority',
        'caption',
        'content',
    ]

    list_per_page = 30

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

admin.site.register(Snippet, SnippetAdmin)


class SnippetTextInline(admin.TabularInline):
    form = SnippetTextForm
    model = Snippet
    extra = 0


class SnippetImageInline(admin.TabularInline):
    form = SnippetImageForm
    model = Snippet
    extra = 0


class SnippetVideoInline(admin.TabularInline):
    form = SnippetVideoForm
    model = Snippet
    extra = 0


class ArticleAdmin(admin.ModelAdmin):

    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size': 120})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 30, 'cols': 120})},
    }

    list_display = (
        'id',
        'uuid',
        'flavor',
        'featured',
        'status',
        'author',
        'editor',
        'headline',
        'description',
        'published_at',
        'updated_at',
        'created_at',
    )

    search_fields = [
        'id',
        'uuid',
        'status',
        'author__email',
        'editor__email',
        'headline',
        'description',
    ]

    list_per_page = 30

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

admin.site.register(Article, ArticleAdmin)


class TrackAdmin(admin.ModelAdmin):
    list_display = ["id", "article", "hit", "view", "like", "updated_at"]
admin.site.register(Track, TrackAdmin)


# Tags
try:
    admin.site.unregister(Tag)
except admin.sites.NotRegistered:
    pass


class ContentTaggedItemInline(admin.StackedInline):
    model = ContentTaggedItem


class ContentTagAdmin(admin.ModelAdmin):
    inlines = [
        ContentTaggedItemInline
    ]
    list_display = ["name", "slug"]
    ordering = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}

admin.site.register(ContentTag, ContentTagAdmin)


class CategoryTaggedItemInline(admin.StackedInline):
    model = CategoryTaggedItem


class CategoryTagAdmin(admin.ModelAdmin):
    inlines = [
        CategoryTaggedItemInline
    ]
    list_display = ["name", "slug"]
    ordering = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}

admin.site.register(CategoryTag, CategoryTagAdmin)


class TargetingTaggedItemInline(admin.StackedInline):
    model = TargetingTaggedItem


class TargetingTagAdmin(admin.ModelAdmin):
    inlines = [
        TargetingTaggedItemInline
    ]
    list_display = ["name", "slug"]
    ordering = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}

admin.site.register(TargetingTag, TargetingTagAdmin)
