from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    """
    Configuration entry point for the site specific app
    """
    label = name = 'siteware'
    verbose_name = "SiteSpecifics"
