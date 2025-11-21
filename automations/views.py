from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Automation
from .forms import AutomationForm

class AutomationListView(LoginRequiredMixin, ListView):
    """
    Lista todas as automações do usuário logado.
    """
    model = Automation
    template_name = 'automation_list.html'
    context_object_name = 'automations'

    def get_queryset(self):
        # IMPORTANTE: Filtra para retornar apenas as automações do dono da conta
        return Automation.objects.filter(user=self.request.user).order_by('-created_at')


class AutomationCreateView(LoginRequiredMixin, CreateView):
    """
    Formulário para criar uma nova automação.
    """
    model = Automation
    form_class = AutomationForm
    template_name = 'automation_create.html'
    success_url = reverse_lazy('automation_list')

    def form_valid(self, form):
        # Antes de salvar, define o usuário logado como dono da automação
        form.instance.user = self.request.user
        return super().form_valid(form)


class AutomationUpdateView(LoginRequiredMixin, UpdateView):
    """
    Formulário para editar uma automação existente.
    """
    model = Automation
    form_class = AutomationForm
    template_name = 'automation_update.html'
    success_url = reverse_lazy('automation_list')

    def get_queryset(self):
        # Segurança: Garante que o usuário só pode editar as automações DELE
        return Automation.objects.filter(user=self.request.user)


class AutomationDeleteView(LoginRequiredMixin, DeleteView):
    """
    Página de confirmação para deletar uma automação.
    """
    model = Automation
    template_name = 'automation_confirm_delete.html'
    success_url = reverse_lazy('automation_list')
    context_object_name = 'automation'

    def get_queryset(self):
        # Segurança: Garante que o usuário só pode deletar as automações DELE
        return Automation.objects.filter(user=self.request.user)