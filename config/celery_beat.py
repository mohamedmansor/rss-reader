from celery.schedules import crontab


def setup_periodic_tasks(app):
    app.conf.beat_schedule = {
        "refresh-feeds-and-posts": {
            "task": "rrs_reader.feed.tasks.periodic_update_feeds_task",
            "schedule": crontab(minute="*/5"),  # every 5 minutes
        },
    }
