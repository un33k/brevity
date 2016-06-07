from django.core.urlresolvers import reverse_lazy

from toolware.utils.mixin import LoginRequiredMixin


from contactware.views import ContactFormView
from contactware.views import ContactMessageSentView

from ..forms import ApprovalForm
from .. import utils as util


class ApprovalFormView(LoginRequiredMixin, ContactFormView):
    """
    Create Approval Form.
    """
    form_class = ApprovalForm
    template_name = util.get_template_path('approval/form.html')
    success_url = reverse_lazy('portal:approval_confirmation_sent_view')


class ContactMessageSentView(LoginRequiredMixin, ContactMessageSentView):
    """
    Approval Message sent
    """
    template_name = util.get_template_path('approval/confirmation.html')
