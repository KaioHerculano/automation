from django import forms
from .models import Automation

class AutomationForm(forms.ModelForm):
    class Meta:
        model = Automation
        fields = ['name', 'platform', 'channel_identifier', 'discord_webhook_url', 'is_active']
        
        # Aqui definimos a aparência (Tailwind) para cada campo
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border',
                'placeholder': 'Ex: Live de Gameplay'
            }),
            'platform': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border bg-white'
            }),
            'channel_identifier': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border',
                'placeholder': '@usuario (TikTok) ou ID do Canal (YouTube)'
            }),
            'discord_webhook_url': forms.URLInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border',
                'placeholder': 'https://discord.com/api/webhooks/...'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
            }),
        }