from django.contrib.auth import get_user_model
from django.db.models import signals
from django.apps import AppConfig as DjangoAppConfig

from .utils.common import get_api_namespace

APP_NAMESPACE = get_api_namespace(__name__)


class AppConfig(DjangoAppConfig):
    """
    Configuration entry point for the api version one app
    """
    label = name = APP_NAMESPACE
    verbose_name = APP_NAMESPACE + 'application'

    def ready(self):
        from .receivers import profile_init
        signals.post_save.connect(profile_init, sender=get_user_model(),
            dispatch_uid='{}.receivers.profile_init'.format(APP_NAMESPACE))
