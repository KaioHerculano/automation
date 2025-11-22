from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# Importando model de outra app para fazer a contagem
from automations.models import Automation 

class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        plan_name = "Grátis (Padrão)"
        limit = 1
        price = 0.00
        
        # Acessa o perfil via relacionamento reverso
        if hasattr(user, 'profile') and user.profile.plan:
            plan = user.profile.plan
            plan_name = plan.name
            limit = plan.max_automations
            price = plan.price
            
        current_count = Automation.objects.filter(user=user).count()
        
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