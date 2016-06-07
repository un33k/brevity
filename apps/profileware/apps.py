from django.db.models import signals
from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    """
    Configuration entry point for the profiles app
    """
    label = name = 'profileware'
    verbose_name = "User Profiles"

    def ready(self):
        """
        App is imported and ready, so bootstrap it.
        """
        from .models import UserProfile
        from . import receivers as rcv

        signals.post_save.connect(rcv.create_tracker,
            sender=UserProfile)

        try:
            from tracware.models import Trac
        except ImportError:
            pass
        else:
            signals.post_save.connect(rcv.profile_trac_on_create,
                sender=Trac)

            signals.pre_delete.connect(rcv.profile_trac_on_delete,
                sender=Trac)
