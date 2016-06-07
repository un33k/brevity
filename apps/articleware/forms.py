from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from autocomplete_light.contrib.taggit_field import TaggitWidget

from toolware.utils.generic import get_uuid
from toolware.utils.mixin import CleanSpacesMixin

from .models import Article
from .models import Snippet
from .models import Image
from .models import Video
from .models import CategoryTag
from .models import TargetingTag
from .models import ContentTag

from . import defaults as defs
from . import utils as util

User = get_user_model()


class ArticleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        initial['flavor'] = Article.ARTICLE_FLAVOR_ARTICLE
        kwargs['initial'] = initial
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['headline'].widget.attrs['placeholder'] = 'Title of your article'
        self.fields['headline'].widget.attrs['class'] = 'article-headline'
        self.fields['headline'].widget.attrs['autofocus'] = ''
        self.fields['categories'].required = True
        self.fields['tags'].required = True
        self.fields['flavor'].widget = forms.HiddenInput()
        if not self.instance or not self.instance.id:
            self.fields['status'].widget = forms.HiddenInput()

    def _clean_taggables(self, model_class, max_num, name):
        items = []
        for item in self.cleaned_data[name]:
            if item not in items:
                try:
                    item = model_class.objects.get(name__iexact=item)
                except model_class.DoesNotExist:
                    if not util.is_article_action_authorized(self.request, name):
                        raise forms.ValidationError(
                            _("Insufficient permissions to create {} ({}).".format(name, item)))
                items.append(item)
        if len(items) > max_num:
            raise forms.ValidationError(_("Article can only have up-to {} {}.".format(
                max_num, name)))
        return items

    def clean_categories(self):
        tags = self._clean_taggables(CategoryTag,
            defs.ARTICLEWARE_MAX_CATEGORIES_PER_ARTICLE, 'categories')
        return tags

    def clean_targets(self):
        tags = self._clean_taggables(TargetingTag, defs.ARTICLEWARE_MAX_TARGETS_PER_ARTICLE, 'targets')
        return tags

    def clean_tags(self):
        tags = self._clean_taggables(ContentTag, defs.ARTICLEWARE_MAX_TAGS_PER_ARTICLE, 'tags')
        return tags

    def clean_headline(self):
        headline = self.cleaned_data["headline"].strip().strip('.')
        if not headline:
            raise forms.ValidationError(_("Article headline is incomplete."))
        if self.instance:
            count = Article.objects \
                .filter(author=self.request.user) \
                .filter(headline__iexact=headline) \
                .filter(flavor=Article.ARTICLE_FLAVOR_ARTICLE) \
                .exclude(id=self.instance.id) \
                .count()
            if count > 0:
                raise forms.ValidationError(_("You have an article with same headline already."))
        return headline

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status == Article.ARTICLE_STATUS_PUBLIC:
            if self.instance.has_warning:
                raise forms.ValidationError(_("Article has warning or is incomplete. Add at least one text snippet"))
        return status

    class Meta:
        model = Article
        fields = (
            'headline',
            'categories',
            'tags',
            'flavor',
            'status',
        )
        widgets = {
            'categories': TaggitWidget('CategoryTagAutocomplete'),
            'tags': TaggitWidget('ContentTagAutocomplete'),
        }


class ArticleBlogForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        initial['flavor'] = Article.ARTICLE_FLAVOR_BLOG
        kwargs['initial'] = initial
        super(ArticleBlogForm, self).__init__(*args, **kwargs)
        self.fields['headline'].widget.attrs['placeholder'] = 'Title of your blog post'
        self.fields['headline'].widget.attrs['class'] = 'article-headline'
        self.fields['headline'].widget.attrs['autofocus'] = ''
        self.fields['flavor'].widget = forms.HiddenInput()
        self.fields['tags'].required = True
        if not self.instance or not self.instance.id:
            self.fields['status'].widget = forms.HiddenInput()

    def _clean_taggables(self, model_class, max_num, name):
        items = []
        for item in self.cleaned_data[name]:
            if item not in items:
                try:
                    item = model_class.objects.get(name__iexact=item)
                except model_class.DoesNotExist:
                    if not util.is_article_action_authorized(self.request, name):
                        raise forms.ValidationError(
                            _("Insufficient permissions to create {} ({}).".format(name, item)))
                items.append(item)
        if len(items) > max_num:
            raise forms.ValidationError(_("Blog posts can only have up-to {} {}.".format(
                max_num, name)))
        return items

    def clean_tags(self):
        tags = self._clean_taggables(ContentTag, defs.ARTICLEWARE_MAX_TAGS_PER_ARTICLE, 'tags')
        return tags

    def clean_headline(self):
        headline = self.cleaned_data["headline"].strip().strip('.')
        if not headline:
            raise forms.ValidationError(_("Blog post headline is incomplete."))
        if self.instance:
            count = Article.objects \
                .filter(author=self.request.user) \
                .filter(headline__iexact=headline) \
                .filter(flavor=Article.ARTICLE_FLAVOR_BLOG) \
                .exclude(id=self.instance.id) \
                .count()
            if count > 0:
                raise forms.ValidationError(_("You have a blog post with same headline already."))
        return headline

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status == Article.ARTICLE_STATUS_PUBLIC:
            if self.instance.has_warning:
                raise forms.ValidationError(_("Blog post has warning or is incomplete. Add at least one text snippet"))
        return status

    class Meta:
        model = Article
        fields = (
            'headline',
            'tags',
            'flavor',
            'status',
        )
        widgets = {
            'categories': TaggitWidget('CategoryTagAutocomplete'),
            'tags': TaggitWidget('ContentTagAutocomplete'),
        }


class ArticlePageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        initial['flavor'] = Article.ARTICLE_FLAVOR_PAGE
        kwargs['initial'] = initial
        super(ArticlePageForm, self).__init__(*args, **kwargs)
        self.fields['headline'].widget.attrs['placeholder'] = 'Title of your flat page'
        self.fields['headline'].widget.attrs['class'] = 'article-headline'
        self.fields['headline'].widget.attrs['autofocus'] = ''
        self.fields['status'].choices = [(x, x) for x in [Article.ARTICLE_STATUS_PRIVATE, Article.ARTICLE_STATUS_UNLISTED]]
        self.fields['flavor'].widget = forms.HiddenInput()
        if not self.instance or not self.instance.id:
            self.fields['status'].widget = forms.HiddenInput()

    def clean_headline(self):
        headline = self.cleaned_data["headline"].strip().strip('.')
        if not headline:
            raise forms.ValidationError(_("Page headline is incomplete."))
        if self.instance:
            count = Article.objects \
                .filter(headline__iexact=headline) \
                .filter(flavor=Article.ARTICLE_FLAVOR_PAGE) \
                .exclude(id=self.instance.id) \
                .count()
            if count > 0:
                raise forms.ValidationError(_("A flat page with same headline exists."))
        return headline

    class Meta:
        model = Article
        fields = (
            'headline',
            'flavor',
            'status',
        )


class SnippetForm(forms.ModelForm):
    """
    Snippet Generic Form
    """
    class Meta:
        model = Snippet
        fields = '__all__'


class SnippetTextForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        initial['type'] = Snippet.SNIPPET_TYPE_TEXT
        kwargs['initial'] = initial
        super(SnippetTextForm, self).__init__(*args, **kwargs)
        self.auto_id = False
        self.fields['content'].widget.attrs.update({'id': get_uuid(12, 4)})
        self.fields['content'].widget.attrs.update({'class': 'wysiwyg text-content'})
        self.fields['content'].widget.attrs['autofocus'] = ''
        self.fields['article'].widget = forms.HiddenInput()
        self.fields['type'].widget = forms.HiddenInput()

    def clean_content(self):
        content = self.cleaned_data["content"]

        if util.is_sanitized_html_blank(content):
            raise forms.ValidationError(_("Text snippets must have content."))

        self.sanitization_required = util.sanitization_required(content)
        content = util.get_sanitized_html(content)

        return content

    class Meta:
        model = Snippet
        fields = (
            'type',
            'content',
            'article'
        )


class SnippetImageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        initial['type'] = Snippet.SNIPPET_TYPE_IMAGE
        kwargs['initial'] = initial
        super(SnippetImageForm, self).__init__(*args, **kwargs)
        self.fields['caption'].widget.attrs.update({'id': get_uuid(12, 4)})
        self.fields['caption'].widget.attrs.update({'class': 'image-caption'})
        self.fields['caption'].widget.attrs['autofocus'] = ''
        self.fields['caption'].help_text = _('Brief explanation & source of images.')
        self.fields['article'].widget = forms.HiddenInput()
        self.fields['type'].widget = forms.HiddenInput()

    def clean_caption(self):
        caption = self.cleaned_data["caption"].strip(' ').strip('.')
        self.sanitization_required = util.sanitization_required(caption, allowed_tags=[])
        caption = util.get_sanitized_html(caption, allowed_tags=[])
        return caption

    class Meta:
        model = Snippet
        fields = (
            'type',
            'caption',
            'article'
        )


class SnippetVideoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        initial['type'] = Snippet.SNIPPET_TYPE_VIDEO
        kwargs['initial'] = initial
        super(SnippetVideoForm, self).__init__(*args, **kwargs)
        self.fields['caption'].widget.attrs.update({'id': get_uuid(12, 4)})
        self.fields['caption'].widget.attrs.update({'class': 'video-caption'})
        self.fields['caption'].widget.attrs['autofocus'] = ''
        self.fields['caption'].help_text = _('Brief explanation & source of videos.')
        self.fields['article'].widget = forms.HiddenInput()
        self.fields['type'].widget = forms.HiddenInput()

    def clean_caption(self):
        caption = self.cleaned_data["caption"].strip(' ').strip('.')
        self.sanitization_required = util.sanitization_required(caption, allowed_tags=[])
        caption = util.get_sanitized_html(caption, allowed_tags=[])
        return caption

    class Meta:
        model = Snippet
        fields = (
            'type',
            'caption',
            'article'
        )


class SnippetMapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        initial['type'] = Snippet.SNIPPET_TYPE_MAP
        kwargs['initial'] = initial
        super(SnippetMapForm, self).__init__(*args, **kwargs)
        self.fields['caption'].widget.attrs.update({'id': get_uuid(12, 4)})
        self.fields['caption'].widget.attrs.update({'class': 'map-caption'})
        self.fields['caption'].widget.attrs['autofocus'] = ''
        self.fields['caption'].help_text = _('Brief explanation & source of map.')
        self.fields['article'].widget = forms.HiddenInput()
        self.fields['content'].widget = forms.HiddenInput()
        self.fields['type'].widget = forms.HiddenInput()

    def clean_caption(self):
        caption = self.cleaned_data["caption"].strip(' ').strip('.')
        self.sanitization_required = util.sanitization_required(caption, allowed_tags=[])
        caption = util.get_sanitized_html(caption, allowed_tags=[])
        return caption

    class Meta:
        model = Snippet
        fields = (
            'type',
            'content',
            'caption',
            'article'
        )


class ImageForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = '__all__'


class VideoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VideoForm, self).__init__(*args, **kwargs)
        self.fields['snippet'].widget = forms.HiddenInput()
        self.fields['vid'].widget = forms.HiddenInput()
        self.fields['link'].widget.attrs['autofocus'] = ''

    def clean_link(self):
        link = self.cleaned_data["link"]
        provider = util.get_video_provider_by_url(link)
        if provider is None:
            raise forms.ValidationError(_("Video provider is not supported."))
        link, self.video_id = util.get_youtube_info(link)

        count = Video.objects.filter(snippet=self.cleaned_data["snippet"]).count()
        if count >= defs.ARTICLEWARE_MAX_VIDEOS_PER_SNIPPET:
            raise forms.ValidationError(_("Max number of videos per snippet is {}".format(
                defs.ARTICLEWARE_MAX_VIDEOS_PER_SNIPPET)))
        return link

    def clean_full(self):
        self.clean_link()
        self.cleaned_data["vid"] = self.video_id
        return self.cleaned_data

    class Meta:
        model = Video
        fields = (
            'snippet',
            'link',
            'vid',
        )
