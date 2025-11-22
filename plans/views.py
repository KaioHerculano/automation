from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class UpgradePageView(LoginRequiredMixin, TemplateView):
    template_name = 'upgrade_contact.html'

class TermsView(TemplateView):
    template_name = 'terms.html'

class PrivacyView(TemplateView):
    template_name = 'privacy.html'