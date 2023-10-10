from celery.schedules import crontab


def setup_periodic_tasks(app):
    app.conf.beat_schedule = {
        'update-feeds-and-items': {
            'task': 'rss_feed.feed.tasks.auto_refresh_followed_feeds',
            'schedule': crontab(minute='*/5'),  # every 5 minutes
        }
    }
