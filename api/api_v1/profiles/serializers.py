import logging

from django.utils import six
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from rest_framework import serializers

from ..utils.common import get_url_name

log = logging.getLogger(__name__)
User = get_user_model()


class ProfileReadSerializerMixin(serializers.ModelSerializer):
    """
    Profile serializer mixin.
    """
    web_url = serializers.SerializerMethodField()
    api_url = serializers.HyperlinkedIdentityField(lookup_field='pk',
        view_name=get_url_name(__name__, 'api-profile-retrieve'))

    def get_web_url(self, obj):
        """
        Return profile's web URL: (WEB)
        """
        request = self.context.get('request')
        return request.build_absolute_uri(obj.get_absolute_url())


class ProfileReadAnonymousSerializer(ProfileReadSerializerMixin):
    """
    Profile serializer: anonymous requests.
    """

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'public_email',
            'company',
            'website',
            'location',
            'web_url',
            'api_url',
        )


class ProfileReadAuthenticatedSerializer(ProfileReadSerializerMixin):
    """
    Profile serializer: authenticated requests.
    """

    email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'web_url',
            'api_url',
            'bio',
            'public_email',
            'company',
            'website',
            'location',
            'last_login',
            'updated_on',
            'created_on',
        )

    def get_email(self, obj):
        """
        Return email if self/superuser is set.
        """
        request = self.context.get('request')
        if request.user.is_superuser or request.user.id == obj.id:
            return obj.email
        return ''


class ProfileCreateSerializer(ProfileReadSerializerMixin):
    """
    Profile serializer for creating a user instance.
    """
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password',
            'username',
            'first_name',
            'last_name',
            'web_url',
            'api_url',
            'bio',
            'public_email',
            'company',
            'website',
            'location',
            'last_login',
            'updated_on',
            'created_on',
        )
        read_only_fields = (
            'id',
            'last_login',
            'updated_on',
            'created_on',
        )
        extra_kwargs = {'password': {'write_only': True}}


class ProfileUpdateSerializer(ProfileReadSerializerMixin):
    """
    Profile serializer for updating a user instance.
    """
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'web_url',
            'api_url',
            'bio',
            'public_email',
            'company',
            'website',
            'location',
            'last_login',
            'updated_on',
            'created_on',
        )
        read_only_fields = (
            'id',
            'last_login',
            'updated_on',
            'created_on',
        )


class ProfilePasswordChangeSerializer(serializers.Serializer):
    """
    Profile serializer for changing an account password.
    """
    current_password = serializers.CharField(required=False)
    new_password = serializers.CharField()
    logout_other_sessions = serializers.BooleanField(default=False)


class ProfilePasswordClearSerializer(serializers.Serializer):
    """
    Profile serializer for clearing an account password.
    """
    pass
