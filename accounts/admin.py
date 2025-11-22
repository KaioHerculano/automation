from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # Adicionei 'status_assinatura' para ver fácil se tá vencido
    list_display = ('user', 'plan', 'plan_expires_at', 'status_assinatura')
    list_filter = ('plan',)
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',) # Muito bom para performance se tiver muitos usuários
    
    def status_assinatura(self, obj):
        if obj.is_plan_active():
            return "✅ Ativo"
        return "❌ Expirado/Inativo"
    status_assinatura.short_description = "Status da Assinatura"