from . import defaults

from .models import CommentCode


def contextify(request):
    """
    Injects Sitewide optional data into the context.
    """
    commentengine = CommentCode.objects.filter(active=True)
    if commentengine:
        ctx = {
            'SITE_COMMENTS_OBJECT': commentengine[0],
        }
        return ctx
    return {}
