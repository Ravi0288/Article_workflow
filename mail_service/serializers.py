from rest_framework import serializers
from .models import Email_history, Email_notification

# serializers to model
class Email_notification_serializer(serializers.ModelSerializer):
    class Meta:
        model = Email_notification
        fields = '__all__'


class Email_history_serializer(serializers.ModelSerializer):
    class Meta:
        model = Email_history
        fields = '__all__'
