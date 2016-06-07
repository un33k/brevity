import logging

from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ..utils.throttles import BurstRateThrottle
from ..utils.throttles import SustainedRateThrottle


log = logging.getLogger(__name__)


class GenericsCsrfAPIView(views.APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (BurstRateThrottle, SustainedRateThrottle,)

    @method_decorator(ensure_csrf_cookie)
    def post(self, request, format=None):
        csrf_token = get_token(request)
        return Response({'csrf_token': csrf_token})
