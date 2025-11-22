from django.contrib import admin
from .models import Automation, NotificationLog, Plan, UserProfile

# --- CONFIGURAÇÃO DE AUTOMAÇÕES ---
@admin.register(Automation)
class AutomationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'user', 
        'platform', 
        'channel_identifier', 
        'is_active', 
        'last_status', 
        'updated_at'
    )
    
    list_filter = ('platform', 'is_active', 'last_status', 'created_at')
    search_fields = ('name', 'user__username', 'channel_identifier')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Dados Principais', {
            'fields': ('name', 'user', 'platform', 'channel_identifier', 'is_active')
        }),
        ('Configuração Técnica', {
            'fields': ('discord_webhook_url',),
        }),
        ('Status e Histórico', {
            'fields': ('last_status', 'created_at', 'updated_at'),
        }),
    )

# --- CONFIGURAÇÃO DE LOGS ---
@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('automation', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('automation__name', 'details')
    readonly_fields = ('automation', 'status', 'details', 'timestamp')
    
    def has_add_permission(self, request):
        return False

# --- NOVO: CONFIGURAÇÃO DE PLANOS ---
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_automations', 'price')
    search_fields = ('name',)

# --- NOVO: CONFIGURAÇÃO DE PERFIS DE USUÁRIO ---
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan')
    list_filter = ('plan',)
    search_fields = ('user__username', 'user__email')
    # raw_id_fields ajuda se você tiver milhares de usuários, 
    # pois cria uma caixa de busca em vez de um dropdown gigante.
    raw_id_fields = ('user',)