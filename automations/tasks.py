from celery import shared_task
from django.conf import settings
from .models import Automation, NotificationLog
from discord_webhook import DiscordWebhook, DiscordEmbed
from TikTokLive import TikTokLiveClient
from asgiref.sync import async_to_sync
import requests
import logging
import re

logger = logging.getLogger(__name__)

def check_tiktok_live(username):
    """
    Verifica se um usuário do TikTok está ao vivo usando a lib oficial.
    """
    try:
        clean_user = username.replace("@", "")
        client = TikTokLiveClient(unique_id=clean_user)
        is_live = async_to_sync(client.is_live)()
        
        logger.info(f"[DEBUG] TikTok Check para '{clean_user}': is_live={is_live}")
        
        return is_live, f"Live de {clean_user}", None
        
    except Exception as e:
        logger.error(f"Erro ao verificar TikTok para '{username}': {e}")
        return False, "", None

def check_youtube_live(channel_id):
    """
    Verifica se um canal do YouTube está ao vivo via Web Scraping (Sem API Key).
    Vantagem: Sem limite de cota diária.
    """
    url = f"https://www.youtube.com/channel/{channel_id}/live"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)

        if response.status_code != 200:
            logger.warning(f"YouTube retornou status {response.status_code} para o canal {channel_id}")
            return False, "", None

        html = response.text

        if '"isLive":true' in html:
            logger.info(f"[DEBUG] YouTube Check '{channel_id}': LIVE DETECTADA! (isLive:true found)")
            title_search = re.search(r'<title>(.*?)- YouTube</title>', html)
            title = title_search.group(1).strip() if title_search else "Live no YouTube"
            thumb_search = re.search(r'"thumbnailUrl":["\'](.*?)["\']', html)
            thumbnail = thumb_search.group(1) if thumb_search else None
            
            return True, title, thumbnail

        logger.info(f"[DEBUG] YouTube Check '{channel_id}': Offline (isLive:true not found)")
        return False, "", None

    except Exception as e:
        logger.error(f"Erro ao fazer scraping do YouTube para '{channel_id}': {e}")
        return False, "", None

def send_discord_alert(automation, is_starting, title, thumbnail_url):
    if not automation.discord_webhook_url:
        return False, "URL do Webhook ausente"

    webhook = DiscordWebhook(url=automation.discord_webhook_url)
    
    if is_starting:
        embed_color = '00FF00'
        status_msg = "🔴 LIVE INICIADA!"
        desc = f"A live **{title}** começou no {automation.get_platform_display()}!"
    else:
        embed_color = '808080'
        status_msg = "⚫ LIVE ENCERRADA!"
        desc = f"A live no {automation.get_platform_display()} terminou. Obrigado a todos!"

    embed = DiscordEmbed(title=status_msg, description=desc, color=embed_color)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
        
    link = ""
    if automation.platform == 'TIKTOK':
        link = f"https://www.tiktok.com/@{automation.channel_identifier.replace('@', '')}/live"
    elif automation.platform == 'YOUTUBE':
        link = f"https://www.youtube.com/channel/{automation.channel_identifier}/live"
    
    embed.add_embed_field(name="Assistir agora", value=f"[Clique aqui para entrar]({link})")
    embed.set_footer(text=f"Bot LiveSync - Automação: {automation.name}")
    embed.set_timestamp()
    webhook.add_embed(embed)
    
    try:
        webhook.execute()
        return True, "Enviado com sucesso"
    except Exception as e:
        logger.error(f"Falha no Discord: {e}")
        return False, str(e)

@shared_task
def process_automation(automation_id):
    try:
        automation = Automation.objects.get(id=automation_id)
    except Automation.DoesNotExist:
        return "Automação não encontrada"

    is_live = False
    title = ""
    thumbnail = ""

    if automation.platform == 'TIKTOK':
        is_live, title, thumbnail = check_tiktok_live(automation.channel_identifier)
    elif automation.platform == 'YOUTUBE':
        is_live, title, thumbnail = check_youtube_live(automation.channel_identifier)

    current_status = 'ONLINE' if is_live else 'OFFLINE'
    previous_status = automation.last_status

    if current_status == 'ONLINE' and previous_status != 'ONLINE':
        success, msg = send_discord_alert(automation, True, title, thumbnail)
        NotificationLog.objects.create(automation=automation, status='SUCCESS' if success else 'FAILURE', details=msg)
        
    elif current_status == 'OFFLINE' and previous_status == 'ONLINE':
        success, msg = send_discord_alert(automation, False, title, thumbnail)
        NotificationLog.objects.create(automation=automation, status='SUCCESS' if success else 'FAILURE', details=msg)

    if previous_status != current_status:
        automation.last_status = current_status
        automation.save(update_fields=['last_status'])
        return f"Status atualizado para {current_status}"
    
    return "Status inalterado"

@shared_task
def scheduler_beat():
    active_automations = Automation.objects.filter(is_active=True)
    for auto in active_automations:
        process_automation.delay(auto.id)
    return f"Verificando {active_automations.count()} automações."