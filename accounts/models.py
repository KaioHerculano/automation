from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from plans.models import Plan


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Plano Atual")
    
    # Campo de expiração
    plan_expires_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Expiração do Plano"
    )

    def is_plan_active(self):
        """Verifica se o plano é válido (existe e não expirou)"""
        if not self.plan:
            return False
        # Se não tem data de expiração, assumimos que é vitalício (ou o plano Free)
        if not self.plan_expires_at:
            return True
        # Verifica se a data de expiração é futura
        return self.plan_expires_at > timezone.now()

    def __str__(self):
        return f"Perfil de {self.user.username}"

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"