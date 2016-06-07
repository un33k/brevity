from django.shortcuts import render_to_response
from django.views.generic import TemplateView
from django.shortcuts import redirect


class PlainTextView(TemplateView):
    """ View for rendering plain text files """

    def render_to_response(self, context, **kwargs):
        return super(PlainTextView, self).render_to_response(context,
            content_type='text/plain', **kwargs)
