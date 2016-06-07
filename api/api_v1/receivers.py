from rest_framework.authtoken.models import Token


def profile_init(sender, instance, signal, created, **kwargs):
    """
    Creates an authentication token for newly created users.
    """
    if created:
        Token.objects.get_or_create(user=instance)
