from django.db import models
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from rest_framework.decorators import api_view
import requests
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Handle model on 
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


# Prepare new handle number
def make_new_handle():
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
    landing_page_url = "http://search.nal.usda.gov/permalink/01NAL INST/27vehl/alma9916422728207426"
    put_url = "http://192.133.202.73:8000/api/handles/{0}"
    mint_handle_api = "http://192.133.202.73:8000/api/handles/"

    # select next value FOR pid;
    # data to be post to the mint handle api.
    json_data = {
        "handle" : handle,
        "values" : [
            {
                "index" : 1,
                "type"  : "URL",
                "data"  : {
                    "format" : "string",
                    "value"  : url
                }
            },
            {
                "index" : 100,
                "type"  : "HS_ADMIN",
                "data"  : {
                    "format" : "admin",
                    "value": {
                        "handle" : "0.NA/10113",
                        "index" : 300,
                        "permissions" : "111111111111",
                        "legacyByteLength" : True
                    }
                }
            }
        ]
    }

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


# mint_handle view to request for user data
def mint_handles(request):
    default_value = "https://agricola.nal.usda.gov"
    if request.method == 'POST':
        url = request.POST.get('user_input', None)
        # Process the input as needed
        min_handle_main_function(request, url)
    return render(request, 'handles/handle.html', {'default_value': default_value})


# main function to execute handle miniting process
# @api_view(['GET'])
def min_handle_main_function(request, landing_page_url=None):
    # default data for mint url parameters
    data = {
        "url":"https://agricola.nal.usda.gov"
    }

    res = {
        'url' : None
    }

    # if parameter received from url than use the provide url as data for mint url parameter 
    if request.GET.get('url', None):
        res['url'] = request.GET.get('url')
    
    if landing_page_url:
        res['url'] = landing_page_url

    # get the response from main api
    # This url is fixed and thats why its harcoded here
    url = "https://article-workflow-admin-dev.nal.usda.gov/api/mint_handle"

    # if no input value for landing_page_url provided
    if not res['url']:
        try: 
            res = requests.post(url, data=data, verify=False)
            res.raise_for_status() 
        except requests.exceptions.HTTPError as err: 
            context = {
                'heading' : 'Mint Handle',
                'message' : {'error': err.args[0], 'error_code': res.status_code}
                }
            return render(request, 'common/dashboard.html', context=context)
            # return Response({'error': errh.args[0], 'error_code': res.status_code})
    
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
            result = mint_new_handle(make_new_handle, res['url'])
            # return Response("Handle minted successfully")
            # return Response(result)
            context = {
                'heading' : 'Mint Handle',
                'message' : result
             }
            return render(request, 'common/dashboard.html', context=context)


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
                result = mint_new_handle(make_new_handle, 'url')
                results.append(result)

        context = {
            'heading' : 'Mint Handle',
            'message' : results
        }
        return render(request, 'common/dashboard.html', context=context)


    context = {
            'heading' : 'Mint Handle',
            'message' : "The received response seems empty or is not required format"
        }
    return render(request, 'common/dashboard.html', context=context)

