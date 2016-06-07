from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework import permissions

from .utils.common import get_url_name


@api_view(('GET',))
@permission_classes((permissions.AllowAny,))
def api_root(request, format=None):
    api_root = {
        'profiles': reverse_lazy(
            get_url_name(__name__, 'api-profile-list'),
            request=request,
            format=format,
        ),
        'generics': reverse_lazy(
            get_url_name(__name__, 'api-generics-csrf-retrieve'),
            request=request,
            format=format,
        ),
    }
    return Response(api_root)
