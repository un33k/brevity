import six
import requests

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import logout as auth_logout

from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from social.exceptions import AuthException
from social.exceptions import AuthCanceled
from social.exceptions import AuthMissingParameter


class ForceLogoutMiddleware(object):
    def process_request(self, request):
        """
        If user is no longer active, log user out.
        """
        if request.user.is_authenticated() and not request.user.is_active:
            messages.add_message(request, messages.ERROR, _("No such account."))
            auth_logout(request)


class ConvertMessageMiddleware(object):
    def process_request(self, request):
        """
        Check for any message param, if so, convert it to a message object
        """
        message_list = request.GET.getlist('message')
        for msg in message_list:
            messages.add_message(request, messages.ERROR, msg)


class RedirectKnownExceptionMiddleware(SocialAuthExceptionMiddleware):
    """
    Catches social auth exceptions and handles them properly.
    """
    def process_exception(self, request, exception):
        if isinstance(exception, AuthException):
            url = self.get_redirect_uri(request, exception)
            msg = self.get_message(request, exception)
            url += ('?' in url and '&' or '?') + 'message={}'.format(urlquote(msg))
            return redirect(url)
        if isinstance(exception, requests.HTTPError):
            url = self.get_redirect_uri(request, exception)
            msg = _('The authentication provider could not be reached. Please try again')
            url += ('?' in url and '&' or '?') + 'message={}'.format(urlquote(msg))
            return redirect(url)
        raise exception

    def get_message(self, request, exception):
        backend_name = self.get_backend_name(request)
        if isinstance(exception, AuthMissingParameter):
            msg = _('Authentication failed.')
        elif isinstance(exception, AuthCanceled):
            msg = _('Authentication canceled.')
        else:
            msg = six.text_type(exception)
        return '{}: {}'.format(backend_name.capitalize(), msg)

    def get_backend_name(self, request):
        name = ''
        backend = getattr(request, 'backend', None)
        if backend:
            name = getattr(backend, 'name', '')
        return name
