from celery.schedules import crontab


def setup_periodic_tasks(app):
    app.conf.beat_schedule = {
        'auto-refresh-feeds-and-posts': {
            'task': 'rss_reader.feed.tasks.def auto_refresh_followed_feeds',
            'schedule': crontab(minute='*/5'),  # every 5 minutes
        }
    }
