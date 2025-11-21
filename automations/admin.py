from django.contrib import admin
from .models import Automation, NotificationLog


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


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('automation', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('automation__name', 'details')
    readonly_fields = ('automation', 'status', 'details', 'timestamp')

    def has_add_permission(self, request):
        return False
