from django.db import models
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from rest_framework.decorators import api_view
import requests
from rest_framework.response import Response

class Handles(models.Model):
    handle = models.CharField(max_length=100, null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    ttl_type = models.CharField(max_length=100, null=True, blank=True)
    ttl = models.IntegerField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    refs = models.TextField(null=True, blank=True)
    admin_read = models.BooleanField(null=True)
    admin_write = models.BooleanField(null=True)
    pub_read = models.BooleanField(null=True)
    pub_write = models.BooleanField(null=True)


    class Meta:
        app_label = 'handles_data'
        managed = False
        db_table = 'handles'

    def __str__(self):
        return self.handle
    

class HandleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Handles
        fields = '__all__'

class HandleViewSet(ModelViewSet):
    queryset = Handles.objects.all()
    serializer_class = HandleSerializer

# get new handle number
def get_new_handle():
    last_handle = Handles.objects.last()

    # If no record found, auto assign the accession number as 1, Else add 1 to existing accession number
    if not last_handle:
        new_handle = '10113/1'
    else:
        last_handle = last_handle.handle.split('/')[1]
        new_handle = int(last_handle) + 1
        return '10113/' + str(new_handle)


# function to mint new handle
def mint_new_handle(handle, url):

    # mint handle api
    mint_handle_api = "https://agricola.nal.usda.gov"

    # select next value FOR pid;
    # data to be post to the mint handle api.
    json_data = {}

    # sending post request to mint-handle-api to mint new handle
    response = requests.post(mint_handle_api, data=json_data, verify=False)
    data = {
        "message" : "successful",
        "Handle" : handle,
        "URL" : url,
        "code" : response.status_code,
        "new" : True
    }
    # return response based on received http code
    return data
    

# main function to execute handle miniting process
@api_view(['GET'])
def mint_handles(request):
    # get the response from main api
    data = {
        "url":"https://agricola.nal.usda.gov"
    }
    
    url = "http://article-workflow-admin-dev.nal.usda.gov/api/mint_handle"

    try: 
        res = requests.post(url, data=data)
        res.raise_for_status() 
    except requests.exceptions.HTTPError as err:  
        return Response({'error': err.args[0], 'error_code': res.status_code})
    
    # if response received from the api, jsonify it
    res = res.json()
    
    # if the received response has single url
    if type(res['url']) is str:
        qs = Handles.objects.filter(data=res['url'])
        if qs.exists():
            # return Response("No action required. URL is already available in handles")
            return Response(
                {
                    "message" : "successful",
                    "Handle" : qs[0].handle,
                    "URL" : res['url'],
                    "code" : 200,
                    "new" : False
                }
            )
        
        else:
            result = mint_new_handle(get_new_handle, res['url'])
            # return Response("Handle minted successfully")
            return Response(result)


    # if the received response has multiple urls
    if type(res['url']) is list:
        urls = res['url']
        results = []
        for url in urls:
            qs = Handles.objects.filter(data=url)
            if qs.exists():
                results.append(
                    {
                        "message" : "successful",
                        "Handle" : qs[0].handle,
                        "URL" : url,
                        "code" : 200,
                        "new" : False
                    }
                )
            else:
                result = mint_new_handle(get_new_handle, 'url')
                results.append(result)

    return Response("The received record seems empty or is not of correct format", status=400)

