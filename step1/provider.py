from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.signals import request_finished
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from datetime import datetime, timedelta
from django.utils import timezone
import logging
from mail_service.models import Email_notification
from mail_service.views import send_notification
from cryptography.fernet import Fernet
from django.core.exceptions import ValidationError
from django.conf import settings
from model.provider import Providers, Fetch_history, Provider_meta_data_FTP, Provider_meta_data_API



# serializers to models
class Providers_serializer(serializers.ModelSerializer):
    class Meta:
        model = Providers
        fields = '__all__'

class Fetch_history_serializer(serializers.ModelSerializer):
    class Meta:
        model = Fetch_history
        fields = '__all__'


class Provider_meta_data_FTP_serializer(serializers.ModelSerializer):
    class Meta:
        model = Provider_meta_data_FTP
        fields = '__all__'
        # exclude = ('password',)

    # validations method clean implementaion
    def validate(self, attrs):
        instance = Provider_meta_data_FTP(**attrs)
        instance.clean()
        return attrs


class Provider_meta_data_API_serializer(serializers.ModelSerializer):
    class Meta:
        model = Provider_meta_data_API
        fields = '__all__'
        # exclude = ('site_token',)
    
    # validations method clean implementaion
    def validate(self, attrs):
        instance = Provider_meta_data_API(**attrs)
        instance.clean()
        return attrs


# viewsets to models
class Provider_viewset(ModelViewSet):
    queryset = Providers.objects.all()
    serializer_class = Providers_serializer


class Fetch_history_viewset(ModelViewSet):
    queryset = Fetch_history.objects.all()
    serializer_class = Fetch_history_serializer

class Provider_meta_data_FTP_viewset(ModelViewSet):
    queryset = Provider_meta_data_FTP.objects.all()
    serializer_class = Provider_meta_data_FTP_serializer

class Provider_meta_data_API_viewset(ModelViewSet):
    queryset = Provider_meta_data_API.objects.all()
    serializer_class = Provider_meta_data_API_serializer



# triggers to update fetch history. This function to be called automatically to update history of each accesss to FTP's
@receiver(post_save, sender=Provider_meta_data_FTP)
def update_history_for_FTP(sender, instance, created, **kwargs):
    # if record is updated
    if not created:
        # create fetch_history for log purposes
        Fetch_history.objects.create(
            provider = instance.provider,
            status = instance.last_pull_status,
            error_message = instance.last_error_message
        )
        return True


# triggers to update fetch history. This function to be called automatically to update history of each accesss to API's
@receiver(post_save, sender=Provider_meta_data_API)
def update_history_for_API(sender, instance, created, **kwargs):
    # if record is updated
    if not created:
        # create fetch_history for log purposes
        Fetch_history.objects.create(
            provider = instance.provider,
            status = instance.last_pull_status,
            error_message = instance.last_error_message
        )

        # if api is failed send the email.
        if instance.last_pull_status == 'failed':
            # send_notification(instance)
            pass
            
        return True