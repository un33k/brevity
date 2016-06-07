from django.db.models import Q
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

from toolware.utils.mixin import LoginRequiredMixin

from ..models import Article
from ..forms import ArticleBlogForm
from . articles import ArticleAddView
from . articles import ArticleUpdateView

from .. import utils as util
from .. import defaults as defs


class ArticleBlogAddView(ArticleAddView):
    """
    Creates new blog post for this user (author)
    """
    form_class = ArticleBlogForm
    article_flavor = "Blog"

    def get_success_url(self):
        return reverse('articleware:article_blog_update', kwargs={'pk': self.object.id})

    def get_template_names(self):
        template_name = util.get_template_path("blog/main.html")
        return template_name


class ArticleBlogUpdateView(ArticleUpdateView):
    """
    Update new blog post for this user (author)
    """
    form_class = ArticleBlogForm
    article_flavor = "Blog"

    def get_template_names(self):
        template_name = util.get_template_path("blog/main.html")
        return template_name

    def get_ajax_template_name(self):
        template_name = util.get_template_path("blog/form_update.html")
        return template_name


class ArticleBlogListView(LoginRequiredMixin, TemplateView):
    """
    Article Blog List View.
    """
    def get_template_names(self):
        template_name = util.get_template_path("blog/list.html")
        return template_name

    def get_articles(self):
        articles = Article.objects \
            .filter(author=self.request.user) \
            .filter(flavor=Article.ARTICLE_FLAVOR_BLOG) \
            .exclude(Q(headline__isnull=True) | Q(headline__exact='')) \
            .order_by('-updated_at', '-created_at')
        return articles

    def get_context_data(self, **kwargs):
        context = super(ArticleBlogListView, self).get_context_data(**kwargs)
        context['articles'] = self.get_articles()
        return context
