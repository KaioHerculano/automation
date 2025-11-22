from django.db import models
from django.contrib.auth.models import User


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

    def __str__(self):
        return f"Perfil de {self.user.username} - {self.plan.name if self.plan else 'Sem Plano'}"

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"


class Automation(models.Model):


    class PlatformChoices(models.TextChoices):
        TIKTOK = 'TIKTOK', 'TikTok'
        YOUTUBE = 'YOUTUBE', 'YouTube'


    class SatustusChoices(models.TextChoices):
        ONLINE = 'ONLINE', 'Online'
        OFFLINE = 'OFFLINE', 'Offline'
        UNKNOWN = 'UNKNOWN', 'Unknown'

    name = models.CharField(max_length=100, verbose_name="Nome da Automação")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='automations')
    platform = models.CharField(max_length=20, choices=PlatformChoices.choices, verbose_name="Plataforma")
    channel_identifier = models.CharField(max_length=100, verbose_name="Utilizador do TikTok ou ID do Canal do YouTube")
    discord_webhook_url = models.URLField(max_length=500, verbose_name="URL do Webhook do Discord")
    is_active = models.BooleanField(default=True, verbose_name="Automação Ativa?")
    last_status = models.CharField(max_length=20, choices=SatustusChoices.choices, default=SatustusChoices.UNKNOWN, verbose_name="Último Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return f"{self.name} ({self.platform}) - {self.channel_identifier}"


    class Meta:
        verbose_name = "Automação"
        verbose_name_plural = "Automações"
        unique_together = ('user', 'platform', 'channel_identifier')


class NotificationLog(models.Model):


    class LogStatusChoices(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Success'
        FAILURE = 'FAILURE', 'Failure'
    
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora")
    status = models.CharField(max_length=20, choices=LogStatusChoices.choices, verbose_name="Status do Log")
    details = models.TextField(verbose_name="Detalhes do Log")


    def __str__(self):
        return f"Log {self.id} - {self.automation.name} - {self.status} at {self.timestamp}"


    class Meta:
        verbose_name = "Log de Notificação"
        verbose_name_plural = "Logs de Notificações"
        ordering = ['-timestamp']
