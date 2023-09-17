from celery.schedules import crontab

broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/0"
timezone = "Etc/GMT-3"  # Set your desired timezone
broker_connection_retry_on_startup = True

# Schedule all tasks to run every 10 seconds
beat_schedule = {
    "task-1": {
        "task": "tasks.get_daily_socks_proxies",
        "schedule": crontab(minute="*/1"),  # Every 1 minute = 60 seconds
    },
    # "get_perm_socks_usa": {
    #     "task": "tasks.get_perm_socks_usa",
    #     "schedule": crontab(minute="*/1"),  # Every 1 minute = 60 seconds
    # },
    # "get_perm_socks_uk": {
    #     "task": "tasks.get_perm_socks_uk",
    #     "schedule": crontab(minute="*/1"),  # Every 1 minute = 60 seconds
    # },
    # "get_perm_socks_canada": {
    #     "task": "tasks.get_perm_socks_canada",
    #     "schedule": crontab(minute="*/1"),  # Every 1 minute = 60 seconds
    # },
    # "get_perm_socks_germany": {
    #     "task": "tasks.get_perm_socks_germany",
    #     "schedule": crontab(minute="*/1"),  # Every 1 minute = 60 seconds
    # },
}
