from django.core.management.base import BaseCommand
from automations.models import Automation, NotificationLog
from automations.tasks import check_tiktok_live, check_youtube_live, send_discord_alert

class Command(BaseCommand):
    help = 'Força a verificação de todas as lives cadastradas manualmente'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Iniciando verificação manual de lives...")
        
        # Pega todas as automações ativas
        automations = Automation.objects.filter(is_active=True)
        
        if not automations.exists():
            self.stdout.write(self.style.WARNING("⚠ Nenhuma automação ativa encontrada."))
            return

        for auto in automations:
            self.stdout.write(f"Checking: {auto.name} ({auto.get_platform_display()})...", ending=' ')
            
            is_live = False
            title = ""
            thumbnail = ""

            # 1. Verifica na plataforma correta
            if auto.platform == 'TIKTOK':
                is_live, title, thumbnail = check_tiktok_live(auto.channel_identifier)
            elif auto.platform == 'YOUTUBE':
                is_live, title, thumbnail = check_youtube_live(auto.channel_identifier)
            
            status_str = "ONLINE 🔴" if is_live else "OFFLINE ⚫"
            self.stdout.write(status_str)

            # Traduz para o status do banco
            current_status = 'ONLINE' if is_live else 'OFFLINE'

            # 2. Lógica de Notificação (Simula a mudança de estado para testar)
            # Se detectou live e antes estava OFFLINE (ou Unknown), avisa!
            if current_status == 'ONLINE' and auto.last_status != 'ONLINE':
                self.stdout.write(f"   -> Mudança detectada! Enviando Discord para {auto.discord_webhook_url}...")
                success, msg = send_discord_alert(auto, True, title, thumbnail)
                
                if success:
                    self.stdout.write(self.style.SUCCESS("   -> ✅ Notificação enviada!"))
                    NotificationLog.objects.create(automation=auto, status='SUCCESS', details="Manual check: Live iniciada")
                else:
                    self.stdout.write(self.style.ERROR(f"   -> ❌ Erro no Discord: {msg}"))

            # Se a live acabou
            elif current_status == 'OFFLINE' and auto.last_status == 'ONLINE':
                self.stdout.write("   -> Live encerrou. Enviando aviso...")
                send_discord_alert(auto, False, title, thumbnail)
                NotificationLog.objects.create(automation=auto, status='SUCCESS', details="Manual check: Live encerrada")

            # Atualiza o banco
            auto.last_status = current_status
            auto.save()

        self.stdout.write(self.style.SUCCESS("\n🏁 Verificação concluída!"))