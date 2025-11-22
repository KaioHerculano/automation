from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile, Plan

@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """
    Gerencia a criação e atualização do UserProfile.
    Garante que o perfil exista, mesmo para usuários antigos (como seu superuser).
    """
    # Verifica se o usuário já tem um perfil acessível via 'instance.profile'
    # O try/except é a forma mais segura de checar o relacionamento OneToOne reverso
    try:
        instance.profile.save()
    except User.profile.RelatedObjectDoesNotExist:
        # Se caiu aqui, é porque o perfil não existe. Vamos criar!
        
        # Tenta pegar o plano "Free", senão pega o primeiro que achar, ou None
        default_plan = Plan.objects.filter(name="Free").first() or Plan.objects.first()
        
        UserProfile.objects.create(user=instance, plan=default_plan)