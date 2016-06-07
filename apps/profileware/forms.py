
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import PasswordChangeForm
from django.forms.widgets import ClearableFileInput
from django.utils.safestring import mark_safe

from toolware.utils.mixin import CleanSpacesMixin

from .models import UserProfile
from . import defaults as defs


class UserProfileChangeAdminForm(forms.ModelForm):
    """
    Custom User Change Form (Admin Use ONLY)
    """
    email = forms.EmailField(required=True)
    password = ReadOnlyPasswordHashField(
        label=_('Password'),
        help_text=_('Raw passwords are not stored, so there is no way to see '
                    'this user password, but you can change the password '
                    'using <a href="password/">this form</a>.'))

    class Meta:
        model = UserProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserProfileChangeAdminForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserProfileCreationForm(forms.ModelForm):
    """
    Custom User Creation Form
    """
    required_css_class = 'required_field'
    custom_error_messages = {
        'password_mismatch': _('The two password fields did not match.'),
    }

    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput,
        validators=[MinLengthValidator(UserProfile.PASSWORD_MIN_LENGTH)],
        help_text=_('Minimum password length is') + ' ({}).'.format(UserProfile.PASSWORD_MIN_LENGTH)
    )

    password2 = forms.CharField(
        label=_('Password confirmation'),
        widget=forms.PasswordInput,
    )

    class Meta:
        model = UserProfile
        fields = ('email',)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.custom_error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(UserProfileCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserProfilePasswordChangeForm(PasswordChangeForm):
    """Customized password change form"""

    required_css_class = 'required_field'
    custom_error_messages = {
        'too_short': _('Password too short! minimum length is') + " ({}).".format(defs.PASSWORD_MIN_LENGTH),
        'same_as_before': _('New password is too similar to the old one. Please choose a different password.'),
    }

    logout_other_sessions = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super(UserProfilePasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'old_password',
            'new_password1',
            'new_password2'
        ]
        self.fields['logout_other_sessions'].label = _('Log me out of other devices')
        self.fields['logout_other_sessions'].required = False
        self.fields['old_password'].widget.attrs['autofocus'] = ''
        self.fields['old_password'].label = _('Current Password')
        self.fields['old_password'].help_text = _('Please enter your current password.')
        self.fields['new_password1'].help_text = _('Please enter your new password.  Minimum length is') + " ({}).".format(
            defs.PASSWORD_MIN_LENGTH)
        self.fields['new_password2'].help_text = _('Please confirm your new password.')

    def clean_new_password2(self):
        new_password2 = super(UserProfilePasswordChangeForm, self).clean_new_password2()
        if len(new_password2) < defs.PASSWORD_MIN_LENGTH:
            raise forms.ValidationError(self.custom_error_messages['too_short'])
        if self.user.check_password(new_password2):
            raise forms.ValidationError(self.custom_error_messages['same_as_before'])
        return new_password2


class UserProfileUpdateForm(forms.ModelForm):
    """
    Custom User Update Form
    """
    required_css_class = 'required_field'

    def __init__(self, *args, **kwargs):
        super(UserProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['autofocus'] = ''

    class Meta:
        model = UserProfile
        fields = ('email', 'first_name', 'last_name', 'username', 'bio',)


class FormImageWidget(ClearableFileInput):
    """A FileField Widget that shows CDN file link"""
    def __init__(self, attrs={}):
        super(FormImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        thumb = ''
        if value and hasattr(value, 'url'):
            thumb = '<a href="{0}" target="_blank"><img src="{0}" width=120/></a><br />'.format(value.url)
        default = super(FormImageWidget, self).render(name, value, attrs)

        if 'Currently' in default:
            default = default.split('</a>')[1].replace('Change:', '')
        return mark_safe(u''.join([thumb, default]))


class CustomClearableFileInput(FormImageWidget):
    pass


class UserProfileForm(CleanSpacesMixin, forms.ModelForm):
    """
    Custom User Profile Update Form, Simple.
    """
    required_css_class = 'required_field'
    photo = forms.ImageField(required=False, widget=CustomClearableFileInput)

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['autofocus'] = ''

    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'bio', 'photo')


class UserProfilePreferencesForm(forms.ModelForm):
    """
    Custom User Preferences Update Form
    """
    required_css_class = 'required_field'

    def __init__(self, *args, **kwargs):
        super(UserProfilePreferencesForm, self).__init__(*args, **kwargs)
        self.fields['public_email'].widget.attrs['autofocus'] = ''

    class Meta:
        model = UserProfile
        fields = ('public_email', 'website', )
