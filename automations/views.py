from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
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
        user_profile = getattr(request.user, 'profile', None)
        limit = 1
        plan_name = "Grátis (Padrão)"

        if user_profile and user_profile.plan:
            limit = user_profile.plan.max_automations
            plan_name = user_profile.plan.name

        current_count = Automation.objects.filter(user=request.user).count()

        if current_count >= limit:
            return render(request, 'plan_limit_reached.html', {
                'limit': limit,
                'plan_name': plan_name,
                'current_count': current_count
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