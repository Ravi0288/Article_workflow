from django.db import models
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from datetime import datetime

# model to list all email api wise for email notification purpose. This is master table
class Email_notification(models.Model):
    applicable_to = models.TextField(help_text="Enter any name to indentify where this record will be used as foreign key for sending email")
    email_from = models.TextField(help_text="Enter email address of the sender")
    email_to = models.TextField(help_text="Enter list of email addresses of the receivers in this format email-1;email-2;email3;and so on;")
    email_subject = models.TextField(default='Error Occured',
                                     help_text="Email default subject"
                                     )
    email_body = models.TextField(blank=True, null=True,
                                  help_text="Email body. This will be the error message from the exceptions handlers"
                                  )

    def __str__(self) -> str:
        return self.applicable_to
    

# Email history to maintain log of each email sent.
# Each time email will be sent a new entry will be made to this table with failed of success status
class Email_history(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    email_ref = models.ForeignKey(Email_notification, related_name='email_notification' , on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=10, default='success')
    email_subject = models.TextField(default='Error Occured')
    email_body = models.TextField(default='Error Occured')

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