from django.db import models
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from rest_framework.decorators import api_view
import requests
from rest_framework.response import Response

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
    URL = models.TextField()

    class Meta:
        app_label = 'handles_data'
        managed = False
        db_table = 'handle'

    def __str__(self):
        return self.handle
    

class HandleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Handle
        fields = '__all__'

class HandleViewSet(ModelViewSet):
    queryset = Handle.objects.all()
    serializer_class = HandleSerializer


# function to mint new handle
def mint_new_handle(rec):
    x = Handle.objects.create(URL= rec, )

# main function to execute handle miniting process
@api_view(['GET'])
def mint_handles(request):
    # get the response from main api
    data = {"url":"https://agricola.nal.usda.gov"}
    url = "http://article-workflow-admin-dev.nal.usda.gov/api/mint_handle"
    try: 
        res = requests.post(url, data=data)
        res.raise_for_status() 
    except requests.exceptions.HTTPError as errh:  
        return Response({'error': errh.args[0], 'error_code': res.status_code})
    
    # if response received from the api, jsonify it
    res = res.json()
    
    # if the received response has signle url
    if type(res['url']) is str:
        qs = Handle.objects.filter(URL=res['url']).exists()
        if qs:
            return Response("No action required. URL is already available in handles")
        else:
            mint_new_handle("x")
            return Response("Handle minted successfully")


    # if the received response has multiple urls
    i = 0
    if type(res['url']) is list:
        urls = res['url']
        for item in urls:
            qs = Handle.objects.filter(URL=res['url']).exists()
            if qs:
                pass
            else:
                i += 1
                mint_new_handle("x")
        if i==0:
            return Response("No action required. URL is already available in handles")
        else:
            return Response("Total {0} handles minted successfully", i)