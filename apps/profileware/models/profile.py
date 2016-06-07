import uuid

from django.db import models
from django.utils import timezone
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.core.validators import MinLengthValidator
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.db.models.query import QuerySet
from django.core.files.storage import get_storage_class
from django.contrib.staticfiles.storage import staticfiles_storage
from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_delete

from toolware.utils.generic import get_uuid
from adware.models import AdSense

from ..validators import *
from .track import Track
from .. import utils as util
from .. import defaults as defs

DefaultStorage = get_storage_class(defs.PROFILEWARE_STORAGE_CLASS)


class CaseInsensitiveQuerySet(QuerySet):
    """
    Custom QuerySet to treat queries on special field(s) as case insensitive.
    Models fields that should be treated as case-insensitive should be place in
    CASE_INSENSITIVE_FIELDS with in the model class.
    Example: CASE_INSENSITIVE_FIELDS = ['email', 'username',]
    """
    def _filter_or_exclude(self, mapper, *args, **kwargs):
        for f in self.model.CASE_INSENSITIVE_FIELDS:
            if f in kwargs:
                kwargs[f + '__iexact'] = kwargs[f]
                del kwargs[f]
        return super(CaseInsensitiveQuerySet, self)._filter_or_exclude(mapper, *args, **kwargs)


class UserProfileManager(BaseUserManager):
    """
    Custom User Manager Class.
    USERNAME_FIELD is the email field.
    """
    def _create_user(self, email, password, is_staff, is_superuser,
                     **extra_fields):
        """
        Creates and saves a User with the given, email and password.
        """
        if email:
            if password is None:
                # Social users with no password won't be able to request a password, unless
                # has_usable_password() passes
                password = get_uuid(length=20, version=4)
            user = self.model(email=self.normalize_email(email),
                              is_staff=is_staff, is_active=True,
                              is_superuser=is_superuser,
                              last_login=timezone.now(),
                              **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user
        else:
            raise ValueError(_('The given email must be set.'))

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)

    def get_queryset(self):
        return CaseInsensitiveQuerySet(self.model)


@python_2_unicode_compatible
class UserProfile(AbstractBaseUser, PermissionsMixin):
    """
    A custom user class.
    The required fields are: email and password.
    """
    default_storage = DefaultStorage()
    PASSWORD_MIN_LENGTH = defs.PASSWORD_MIN_LENGTH

    email = models.EmailField(
        _('email'),
        db_index=True,
        unique=True,
        help_text=_('Your private email address. We use this to contact you.')
    )

    is_staff = models.BooleanField(
        _('staff member'),
        default=False,
        help_text=_('Designates if the user can log into this admin site.'),
    )

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Inactive users cannot login.'),
    )

    # ### Django specific fields is above this line ###
    created_on = models.DateTimeField(
        _('Date Joined'),
        default=timezone.now,
    )

    updated_on = models.DateTimeField(
        _('Last Updated'),
        auto_now=True,
    )

    username = models.CharField(
        _('username'),
        max_length=defs.PROFILEWARE_USERNAME_MAX_LENGHT,
        unique=True,
        default=util.get_default_username,
        validators=[MinLengthValidator(3), AlphaNumDashValidator,
            MaxLengthValidator(defs.PROFILEWARE_USERNAME_MAX_LENGHT), ],
        help_text=_('Choose alphanumeric and dashes. It cannot begin or end with a dash.'),
    )

    first_name = models.CharField(
        _('first name'),
        max_length=60,
        null=True,
        blank=False,
        help_text=_('Your first name.')
    )

    last_name = models.CharField(
        _('last name'),
        max_length=255,
        null=True,
        blank=False,
        help_text=_('Your last name.')
    )

    bio = models.TextField(
        _('your bio'),
        blank=True,
        validators=[MaxLengthValidator(2000)],
        help_text=_('Your biographical information or background.')
    )

    public_email = models.EmailField(
        _('public email'),
        blank=True,
        help_text=_('Your public email address. Everyone can see this. (Optional)')
    )

    website = models.CharField(
        _('website'),
        max_length=120,
        blank=True,
        help_text=_('Your website address. (Optional)')
    )

    location = models.CharField(
        _('location'),
        max_length=255,
        blank=True,
        help_text=_('Your location or address.')
    )

    company = models.CharField(
        _('company'),
        max_length=120,
        blank=True,
        help_text=_('Your company name.')
    )

    photo = models.ImageField(
        null=True,
        blank=True,
        storage=default_storage,
        upload_to=util.uploadto_user_photo,
        max_length=255,
    )

    # ########## Add new fields above this line #############
    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    CASE_INSENSITIVE_FIELDS = ['email', 'username', 'first_name', 'last_name', 'public_email', ]

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return u'{} [{}]'.format(self.username, self.email)

    @property
    def stars(self):
        stars = self.track.star
        return stars

    def get_absolute_url(self):
        """
        Return public URL for user
        """
        return "/m/{}/".format(self.username)

    def get_short_name(self):
        """
        Returns first name
        """
        return self.first_name

    def get_full_name(self):
        """
        Returns full name
        """
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def full_name(self):
        """
        Returns full name alias
        """
        return self.get_full_name()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this Use
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_user_photo(self):
        if self.photo:
            url = self.photo.url
        else:
            url = staticfiles_storage.url('img/misc/user-icon.png')
        return url

    def remove_old_photo(self):
        if defs.PROFILEWARE_REMOVE_IMAGE_CACHE_ON_DELETION:
            try:
                obj = UserProfile.objects.get(id=self.id)
            except UserProfile.DoesNotExist:
                return
            if obj.photo and self.photo and obj.photo != self.photo:
                obj.photo.delete()

    def save(self, *args, **kwargs):
        """
        Final housekeeping before save
        """
        self.remove_old_photo()
        return super(UserProfile, self).save(*args, **kwargs)


@receiver(pre_delete, sender=UserProfile)
def _image_enforce_single_and_bulk_delete(sender, instance, **kwargs):
    if defs.PROFILEWARE_REMOVE_IMAGE_CACHE_ON_DELETION:
        if instance.photo:
            instance.photo.delete()


# Create a track object on demand if not already created
UserProfile.track = property(lambda self: Track.objects.get_or_create(profile=self)[0])

# Create an AdSense object on demand if not already created
UserProfile.adsense = property(lambda self: AdSense.objects.get_or_create(user=self)[0])
