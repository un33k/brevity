from django.contrib import messages
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect

from toolware.utils.mixin import LoginRequiredMixin
from toolware.utils.mixin import CsrfProtectMixin

from .models import UserProfile
from .forms import UserProfileForm
from .forms import UserProfilePreferencesForm

from . import defaults as defs
from . import utils as util
from . import signals


class AccountIndexView(LoginRequiredMixin, TemplateView):
    """
    Account Index View, serving the account index page.
    """
    def get_template_names(self):
        template_name = util.get_template_path("base.html")
        return template_name


class UserProfileUpdateView(LoginRequiredMixin, CsrfProtectMixin, UpdateView):
    """
    User Profile update view.
    """
    form_class = UserProfileForm
    success_url = reverse_lazy('profileware:account_profile')

    def get_template_names(self):
        template_name = util.get_template_path("profile_update_form.html")
        return template_name

    def get_object(self, queryset=None):
        profile = self.request.user
        return profile

    def form_valid(self, form):
        self.object = form.save()
        messages.add_message(self.request, messages.SUCCESS, _('Your profile was saved'))
        signals.profile_updated.send(sender=UserProfile, request=self.request, user=self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.first_name:
            messages.add_message(self.request, messages.WARNING,
                _('Your account must have short name and full name. Please enter your name now.'))
        return super(UserProfileUpdateView, self).get(*args, **kwargs)


class AccountPreferencesView(LoginRequiredMixin, CsrfProtectMixin, UpdateView):
    """
    Account Settings View, serving the account settings page.
    """
    form_class = UserProfilePreferencesForm
    success_url = reverse_lazy('profileware:account_profile_preferences')

    def get_template_names(self):
        template_name = util.get_template_path("profile_preferences_form.html")
        return template_name

    def get_object(self, queryset=None):
        profile = self.request.user
        return profile

    def form_valid(self, form):
        self.object = form.save()
        messages.add_message(self.request, messages.SUCCESS, _('Your preferences was saved.'))
        signals.profile_updated.send(sender=UserProfile, request=self.request, profile=self.object)
        return HttpResponseRedirect(self.get_success_url())


class AccountSocialAssociationView(LoginRequiredMixin, TemplateView):
    """
    Account Social Associations
    """
    def get_template_names(self):
        template_name = util.get_template_path("profile_social.html")
        return template_name
