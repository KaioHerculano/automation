from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.utils import timezone
from .models import Automation, NotificationLog
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
    template_name = 'automations/automation_create.html'
    success_url = reverse_lazy('automation_list')

    def dispatch(self, request, *args, **kwargs):
        user_profile = getattr(request.user, 'profile', None)
        limit = 0
        plan_name = "Sem Plano Ativo"
        is_expired = False

        if user_profile and user_profile.plan:
            limit = user_profile.plan.max_automations
            plan_name = user_profile.plan.name

            if user_profile.plan_expires_at and user_profile.plan_expires_at < timezone.now():
                is_expired = True

        current_count = Automation.objects.filter(user=request.user).count()

        if is_expired:
            return render(request, 'plan_limit_reached.html', {
                'limit': limit,
                'plan_name': plan_name,
                'current_count': current_count,
                'error_message': f"Seu plano {plan_name} expirou. Renove para continuar."
            })

        if current_count >= limit:
            return render(request, 'plan_limit_reached.html', {
                'limit': limit,
                'plan_name': plan_name,
                'current_count': current_count,
                'error_message': "Você não possui um plano ativo para criar automações." if limit == 0 else None
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
        
        total_automations = Automation.objects.filter(user=user).count()
        active_automations = Automation.objects.filter(user=user, is_active=True).count()
        
        total_notifications = NotificationLog.objects.filter(
            automation__user=user, 
            status='SUCCESS'
        ).count()
        
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
