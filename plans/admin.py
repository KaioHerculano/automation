from django.contrib import admin
from .models import Plan

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_automations', 'price')
    search_fields = ('name',)
    ordering = ('price',)