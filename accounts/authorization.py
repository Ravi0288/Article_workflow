from django.contrib.auth.models import User, Group
from django.db import models
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
import importlib
from django import forms
from django.apps import apps
from django.urls import URLPattern, URLResolver
from django.shortcuts import render, redirect


import importlib
from django.apps import apps
from django.urls import URLPattern, URLResolver

def get_url_names() -> tuple:
    list_of_url_names = []

    for name, app in apps.app_configs.items():
        mod_to_import = f'{name}.urls'
        try:
            urls_module = importlib.import_module(mod_to_import)
            urlpatterns = getattr(urls_module, 'urlpatterns', [])

            for pattern in urlpatterns:
                if isinstance(pattern, URLPattern):
                    if pattern.name:
                        # Add the tuple with both value and human-readable name
                        list_of_url_names.append((pattern.name, pattern.name))
                elif isinstance(pattern, URLResolver):
                    for sub_pattern in pattern.url_patterns:
                        if isinstance(sub_pattern, URLPattern):
                            if sub_pattern.name:
                                list_of_url_names.append((sub_pattern.name, sub_pattern.name))

        except Exception as e:
            # print(f"An error occurred: {ex}")
            pass

    # # Remove duplicates by converting to a set and back to a list
    list_of_url_names = tuple(set(list_of_url_names))


    return list_of_url_names



class Authorization(models.Model):
    groups = models.ManyToManyField(Group)
    menu = models.CharField(max_length=100, choices=get_url_names())


class Authorization_serilalizer(ModelSerializer):
    class Meta:
        model = Authorization
        fields = '__all__'

class Authorization_viewset(ModelViewSet):
    queryset = Authorization.objects.all()
    serializer_class = Authorization_serilalizer



class AuthorizationForm(forms.ModelForm):
    class Meta:
        model = Authorization
        fields = [ 'menu','groups'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['menu'].choices = get_url_names()


def create_authorization(request):
    if request.method == 'POST':
        form = AuthorizationForm(request.POST)
        if form.is_valid():
            form.save()
            context = {
                'heading' : 'Authorization',
                'message' : 'authorization successfully added'
            }
        else:
            context = {
                'heading' : 'Authorization',
                'message' : 'Error Message=' "Ensure correct value is provided for each form fields"
            }
        return render(request, 'common/dashboard.html', context=context)
        
    else:
        form = AuthorizationForm()

    return render(request, 'accounts/create_authorization.html', {'form': form})
