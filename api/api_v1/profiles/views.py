import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework.response import Response
from rest_framework import decorators
from rest_framework import viewsets
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework import views

from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated

from ..utils.permissions import IsOwner
from ..utils.permissions import IsOwnerOrAdmin
from ..utils.throttles import BurstRateThrottle
from ..utils.throttles import SustainedRateThrottle
from ..utils.throttles import ProfileCreateRateThrottle

from .serializers import *

log = logging.getLogger(__name__)
User = get_user_model()


class ProfileViewMixin(object):
    queryset = User.objects.all()
    serializer_class = ProfileReadAnonymousSerializer
    permission_classes = (IsAuthenticated, IsOwner,)
    throttle_classes = (BurstRateThrottle, SustainedRateThrottle,)

    def get_serializer_class(self):
        if self.request.method == "GET":
            if self.request.user.is_authenticated():
                return ProfileReadAuthenticatedSerializer
        return self.serializer_class

    def get_queryset(self):
        if self.request.method == "GET":
            if not self.request.user.is_superuser:
                return User.objects.filter(is_active=True, is_superuser=False)
            if not self.request.user.is_staff:
                return User.objects.filter(is_active=True, is_superuser=False, is_staff=False)
        return self.queryset


class ProfileListAPIView(ProfileViewMixin, generics.ListAPIView):
    """
    Profile List View.
    """
    permission_classes = (AllowAny,)


class ProfileRetrieveAPIView(ProfileViewMixin, generics.RetrieveAPIView):
    """
    Profile Retrieve View.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if self.lookup_field not in self.kwargs:
            if self.lookup_field == 'pk':
                self.kwargs[self.lookup_field] = self.request.user.id
            else:
                self.kwargs[self.lookup_field] = getattr(self.request.user, self.lookup_field, None)
        return self.retrieve(request, *args, **kwargs)


class ProfileCreateAPIView(ProfileListAPIView, generics.CreateAPIView):
    """
    Profile Create View.
    """
    serializer_class = ProfileCreateSerializer
    permission_classes = (AllowAny,)
    throttle_classes = (ProfileCreateRateThrottle,)

    def post_save(self, obj, created=False):
        if created:
            obj.set_password(obj.password)
            obj.save()


class ProfileUpdateAPIView(ProfileRetrieveAPIView, generics.UpdateAPIView):
    """
    Profile Update View.
    """
    serializer_class = ProfileUpdateSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin,)


class ProfileDeleteAPIView(ProfileRetrieveAPIView, generics.DestroyAPIView):
    """
    Profile Delete View.
    """
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin,)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_superuser:
            return Response({'status': _('Cannot delete privileged user via api.')},
                    status.HTTP_403_FORBIDDEN)
        return super(ProfileDeleteAPIView, self).destroy(request, *args, **kwargs)


class ProfilePasswordChangeAPIView(ProfileRetrieveAPIView, generics.GenericAPIView):
    """
    Profile Password Change View.
    """
    custom_messages = {
        'password_invalid': _('Please enter your current password.'),
        'new_password': _('New password is too similar to the old password.'),
        'password_changed': _('Password changed.'),
    }

    def get_serializer_class(self):
        if self.request.method == "GET":
            if self.request.user.is_authenticated():
                return ProfileReadAuthenticatedSerializer
        return ProfilePasswordChangeSerializer

    def post(self, request, format=None):
        user = request.user
        serializer = ProfilePasswordChangeSerializer(data=request.DATA)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        current_password = serializer.data.get('current_password')
        if current_password is None or len(current_password) == 0:
            if user.has_usable_password():  # hint: social registration perhaps?
                return Response({'current_password': self.custom_messages['password_invalid']},
                    status.HTTP_400_BAD_REQUEST)

        elif not user.check_password(current_password):
            return Response({'current_password': self.custom_messages['password_invalid']},
                    status.HTTP_400_BAD_REQUEST)

        new_password = serializer.data.get('new_password')
        if user.check_password(new_password):
            return Response({'new_password': self.custom_messages['new_password']},
                status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'status': self.custom_messages['password_changed']})


class ProfilePasswordClearAPIView(ProfileRetrieveAPIView, generics.GenericAPIView):
    """
    Profile Password Clear View.
    """
    permission_classes = (IsAuthenticated, IsAdminUser,)

    custom_messages = {
        'password_self': _('Cannot clear your own password.'),
        'password_cleared': _('Password cleared.'),
    }

    def get_serializer_class(self):
        if self.request.method == "GET":
            if self.request.user.is_authenticated():
                return ProfileReadAuthenticatedSerializer
        return ProfilePasswordClearSerializer

    def post(self, request, pk=None, format=None):
        user = self.get_object()
        if request.user == user:
            return Response({'status': self.custom_messages['password_self']},
                status.HTTP_400_BAD_REQUEST)
        user.set_unusable_password()
        user.save()
        return Response({'status': self.custom_messages['password_cleared']})
