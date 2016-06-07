from django import forms
from django.utils.translation import ugettext as _

from contactware.forms import ContactForm

from .. import utils as util


class ApprovalForm(ContactForm):
    """
    Approval Form.
    """
    identifier = 'approval'

    def __init__(self, *args, **kwargs):
        super(ApprovalForm, self).__init__(*args, **kwargs)
        self.fields['subject'].widget = forms.HiddenInput()
        self.fields['subject'].initial = _('Approval Request')
        self.fields['message'].widget.attrs['placeholder'] = 'Approval request message'
        self.fields['message'].help_text = _('Why you want to become an approved author and what will you be writing about.')
        self.subject_template = util.get_template_path('approval/message_subject.txt')
        self.body_template = util.get_template_path('approval/message_body.txt')
