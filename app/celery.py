import os
from celery import Celery

# Define as configurações do Django como padrão para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('livesync')

# Lê as configurações do arquivo settings.py (tudo que começar com CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre automaticamente tarefas (tasks.py) em todos os apps instalados
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')