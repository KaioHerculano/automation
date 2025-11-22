from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone # Importante para lidar com datas

# --- MODELOS DE PLANOS E PERFIL ---

class Plan(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nome do Plano")
    max_automations = models.IntegerField(default=1, verbose_name="Limite de Automações")
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Preço Mensal")

    def __str__(self):
        return f"{self.name} ({self.max_automations} automações)"

    class Meta:
        verbose_name = "Plano"
        verbose_name_plural = "Planos"


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


# --- MODELOS DE AUTOMAÇÃO ---

class Automation(models.Model):
    """
    Representa uma regra de notificação criada por um utilizador.
    """

    class PlatformChoices(models.TextChoices):
        TIKTOK = 'TIKTOK', 'TikTok'
        YOUTUBE = 'YOUTUBE', 'YouTube'

    class StatusChoices(models.TextChoices):
        ONLINE = 'ONLINE', 'Online'
        OFFLINE = 'OFFLINE', 'Offline'
        UNKNOWN = 'UNKNOWN', 'Desconhecido'

    # Campos Principais (em Inglês para padronização)
    name = models.CharField(max_length=100, verbose_name="Nome da Automação")
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='automations'
    )
    
    platform = models.CharField(
        max_length=20, 
        choices=PlatformChoices.choices, 
        verbose_name="Plataforma"
    )
    
    channel_identifier = models.CharField(
        max_length=100, 
        verbose_name="Utilizador do TikTok ou ID do Canal do YouTube"
    )
    
    discord_webhook_url = models.URLField(
        max_length=500, 
        verbose_name="URL do Webhook do Discord"
    )
    
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Automação Ativa?"
    )
    
    # Campos de Controle
    last_status = models.CharField(
        max_length=20, 
        choices=StatusChoices.choices, 
        default=StatusChoices.UNKNOWN, 
        verbose_name="Último Status"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return f"{self.name} ({self.get_platform_display()}) - {self.channel_identifier}"

    class Meta:
        verbose_name = "Automação"
        verbose_name_plural = "Automações"
        # Garante unicidade: um usuário não pode ter 2 automações iguais para o mesmo canal/plataforma
        unique_together = ('user', 'platform', 'channel_identifier')


class NotificationLog(models.Model):
    """
    Histórico de envios de notificação.
    """

    class LogStatusChoices(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Sucesso'
        FAILURE = 'FAILURE', 'Falha'
    
    automation = models.ForeignKey(
        Automation, 
        on_delete=models.CASCADE, 
        related_name='logs'
    )
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora")
    
    status = models.CharField(
        max_length=20, 
        choices=LogStatusChoices.choices, 
        verbose_name="Status do Log"
    )
    
    details = models.TextField(verbose_name="Detalhes do Log")

    def __str__(self):
        return f"Log {self.id} - {self.automation.name} - {self.status} em {self.timestamp}"

    class Meta:
        verbose_name = "Log de Notificação"
        verbose_name_plural = "Logs de Notificações"
        ordering = ['-timestamp']