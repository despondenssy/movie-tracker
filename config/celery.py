import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('cinema_tracker')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях
app.autodiscover_tasks()

# Настройка периодических задач
app.conf.beat_schedule = {
    'update-trending-cache': {
        'task': 'movies.tasks.update_trending_cache',
        'schedule': crontab(minute=0),  # Каждый час
    },
    'update-popular-cache': {
        'task': 'movies.tasks.update_popular_cache',
        'schedule': crontab(hour='*/6'),  # Каждые 6 часов
    },
}

app.conf.timezone = 'UTC'
