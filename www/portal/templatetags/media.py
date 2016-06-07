from django import template

register = template.Library()


@register.filter
def optimized_image(request, obj):
    """
    Given a media object with three image sizes `image`, `image_md`, `image_sm`, it
    returns the URL to the image of the proper size based on the client type.
    """
    url = obj.image.url
    if request.user_agent.is_mobile:
        url = obj.image_sm.url
    return url
