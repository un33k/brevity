from django.apps import apps
from django.apps import AppConfig as DjangoAppConfig
from django.utils.translation import ugettext_lazy as _


class AppConfig(DjangoAppConfig):
    """
    Configuration entry point for the portal app, handling the public views
    """
    label = name = 'portal'
    verbose_name = _("Portal App")
