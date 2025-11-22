from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.utils import timezone
from .models import Automation
from .forms import AutomationForm

class AutomationListView(LoginRequiredMixin, ListView):
    model = Automation
    template_name = 'automation_list.html'
    context_object_name = 'automations'

    def get_queryset(self):
        return Automation.objects.filter(user=self.request.user).order_by('-created_at')

class AutomationCreateView(LoginRequiredMixin, CreateView):
    model = Automation
    form_class = AutomationForm
    template_name = 'automation_create.html'
    success_url = reverse_lazy('automation_list')

    def dispatch(self, request, *args, **kwargs):
        # --- LÓGICA DE PROTEÇÃO (LIMITES E VALIDADE) ---
        
        user_profile = getattr(request.user, 'profile', None)
        
        # Valores padrão (Fail-Safe)
        limit = 1
        plan_name = "Grátis (Padrão)"
        is_expired = False

        if user_profile and user_profile.plan:
            limit = user_profile.plan.max_automations
            plan_name = user_profile.plan.name
            
            # Verifica se o plano tem data de validade e se já venceu
            if user_profile.plan_expires_at and user_profile.plan_expires_at < timezone.now():
                is_expired = True

        current_count = Automation.objects.filter(user=request.user).count()
        
        # BLOQUEIO 1: Plano Expirado
        if is_expired:
            return render(request, 'plan_limit_reached.html', {
                'limit': limit,
                'plan_name': plan_name,
                'current_count': current_count,
                'error_message': f"Seu plano {plan_name} expirou. Renove para continuar."
            })

        # BLOQUEIO 2: Limite de Quantidade Atingido
        if current_count >= limit:
            return render(request, 'plan_limit_reached.html', {
                'limit': limit,
                'plan_name': plan_name,
                'current_count': current_count,
                'error_message': None # Usa a mensagem padrão do template
            })
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class AutomationUpdateView(LoginRequiredMixin, UpdateView):
    model = Automation
    form_class = AutomationForm
    template_name = 'automation_update.html'
    success_url = reverse_lazy('automation_list')

    def get_queryset(self):
        return Automation.objects.filter(user=self.request.user)

class AutomationDeleteView(LoginRequiredMixin, DeleteView):
    model = Automation
    template_name = 'automation_confirm_delete.html'
    success_url = reverse_lazy('automation_list')
    context_object_name = 'automation'

    def get_queryset(self):
        return Automation.objects.filter(user=self.request.user)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 1. Estatísticas de Automações
        total_automations = Automation.objects.filter(user=user).count()
        active_automations = Automation.objects.filter(user=user, is_active=True).count()
        
        # 2. Estatísticas de Notificações (Logs) - Assumindo que NotificationLog está importado
        # Se der erro, adicione: from .models import NotificationLog no topo
        from .models import NotificationLog 
        total_notifications = NotificationLog.objects.filter(
            automation__user=user, 
            status='SUCCESS'
        ).count()
        
        # 3. Últimas atividades
        recent_logs = NotificationLog.objects.filter(
            automation__user=user
        ).order_by('-timestamp')[:5]

        context.update({
            'total_automations': total_automations,
            'active_automations': active_automations,
            'total_notifications': total_notifications,
            'recent_logs': recent_logs
        })
        return context


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Valores padrão
        plan_name = "Grátis (Padrão)"
        limit = 1
        price = 0.00
        
        if hasattr(user, 'profile') and user.profile.plan:
            plan = user.profile.plan
            plan_name = plan.name
            limit = plan.max_automations
            price = plan.price
            
        current_count = Automation.objects.filter(user=user).count()
        
        # Cálculo da barra de progresso
        usage_percent = 0
        if limit > 0:
            usage_percent = int((current_count / limit) * 100)
            if usage_percent > 100: usage_percent = 100
        
        context.update({
            'plan_name': plan_name,
            'limit': limit,
            'price': price,
            'current_count': current_count,
            'usage_percent': usage_percent
        })
        
        return context


class UpgradePageView(LoginRequiredMixin, TemplateView):
    template_name = 'upgrade_contact.html'


class TermsView(TemplateView):
    template_name = 'terms.html'


class PrivacyView(TemplateView):
    template_name = 'privacy.html'
