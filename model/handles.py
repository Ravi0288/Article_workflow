from django.db import models
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers

class Handle(models.Model):
    handle = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    data = models.CharField(max_length=100)
    ttl_type = models.CharField(max_length=100)
    ttl = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    refs = models.CharField(max_length=100)
    admin_read = models.CharField(max_length=100)
    admin_write = models.CharField(max_length=100)
    pub_read = models.CharField(max_length=100)
    pub_write = models.CharField(max_length=100)

    class Meta:
        app_label = 'handles_data'
        # managed = False
        db_table = 'handle'

    # def __str__(self):
    #     return self.handle
    

class HandleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Handle
        fields = '__all__'

class HandleViewSet(ModelViewSet):
    queryset = Handle.objects.all()
    serializer_class = HandleSerializer