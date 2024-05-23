from django.shortcuts import render
from .models import Email_history, Email_notification
from .serializers import Email_history_serializer, Email_notification_serializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ModelViewSet
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from datetime import datetime

# viewsets to model
class Email_notification_viewset(ModelViewSet):
    queryset = Email_notification.objects.all()
    serializer_class = Email_notification_serializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.GET
        qs = qs.filter(**params.dict())
        return qs

class Email_history_viewset(ModelViewSet):
    queryset = Email_history.objects.all()
    serializer_class = Email_history_serializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.GET
        qs = qs.filter(**params.dict())
        return qs
    

# Funtion to email.
# This function will send the email and will update the Email_history table
    # instance is the instance of APT/FTP providers model
def send_notification(instance):
    # collect the data from the provided instances
    subject = instance.email_notification.email_subject
    email_from = instance.email_notification.email_from
    email_to = instance.email_notification.email_to
    email_body = instance.last_error_message

    # prepate the email content
    msg = EmailMessage(subject, email_body, email_from, email_to).send()

    # send the email and update the email_history table for log puprposes
    if msg:
        Email_history.objects.create(
            timestamp=datetime.utcnow(), 
            email_ref=instance, 
            status='success',
            email_subject = subject,
            email_body = email_body
            )
    else:
        Email_history.objects.create(
            timestamp=datetime.utcnow(), 
            email_ref=instance, 
            status='failed',
            email_subject = subject,
            email_body = email_body            
            )
        
    return True
