from django.db import models
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from datetime import datetime

# model to list all email api wise for email notification purpose
class Email_notification(models.Model):
    # applicable_to is the name of the group
    applicable_to = models.CharField(blank=True, null=True, max_length=50)
    email_from = models.TextField()
    email_to = models.TextField()
    email_subject = models.TextField(default='Error Occured')
    email_body = models.TextField(default='Error Occured')

    def __str__(self) -> str:
        return self.applicable_to
    
# email history to maintain log of each email sent
class Email_history(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    email_ref = models.ForeignKey(Email_notification, related_name='email_notification' , on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=10, default='success')

    def __str__(self) -> str:
        return self.email_ref.applicable_to + '->' + self.status


# serializers to model
class Email_notification_serializer(serializers.ModelSerializer):
    class Meta:
        model = Email_notification
        fields = '__all__'


class Email_history_serializer(serializers.ModelSerializer):
    class Meta:
        model = Email_history
        fields = '__all__'


# viewsets to model
class Email_notification_viewset(ModelViewSet):
    queryset = Email_notification.objects.all()
    serializer_class = Email_notification_serializer


class Email_history_viewset(ModelViewSet):
    queryset = Email_history.objects.all()
    serializer_class = Email_history_serializer


# Funtion to email.
# This function will send the email and will update the Email_history table
def send_comment_mail_notification(instance, error_msg):
    # collect the data from the provided instances
    message = instance.get('email_body', '')
    subject = instance.get('email_subject', '')
    email_from = instance.get('email_from', '')
    email_to = instance.get('from_to', '')
    subject += subject + '->' + error_msg

    # prepate the email content
    msg = EmailMessage(subject, message, email_from, email_to)

    # send the email and update the email_history table for log puprposes
    try:
        msg.send()
        Email_history.objects.create(timestamp=datetime.utcnow(), email_ref=instance, status='success')
    except:
        Email_history.objects.create(timestamp=datetime.utcnow(), email_ref=instance, status='failed')
    return True