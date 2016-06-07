from django.apps import apps
from django.db.models import signals
from django.apps import AppConfig as DjangoAppConfig
from django.utils.translation import ugettext_lazy as _


class AppConfig(DjangoAppConfig):
    """
    Configuration entry point for the articleware app
    """
    label = name = 'articleware'
    verbose_name = _("Articles")

    def ready(self):
        """
        App is imported and ready, so bootstrap it.
        """
        from .models import Article
        from . import receivers as rcv

        signals.post_migrate.connect(rcv.post_migrate_receiver,
            sender=apps.get_app_config(self.name))

        signals.post_save.connect(rcv.create_tracker,
            sender=Article)

        try:
            from tracware.models import Trac
        except ImportError:
            pass
        else:
            signals.post_save.connect(rcv.article_trac_on_create,
                sender=Trac)

            signals.pre_delete.connect(rcv.article_trac_on_delete,
                sender=Trac)

        rcv.register_autocomplete()
