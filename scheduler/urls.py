from django.urls import path
from .cron import trigger_scheduler

urlpatterns = [
    path('trigger-scheduler/', trigger_scheduler, name='trigger-scheduler'),
]