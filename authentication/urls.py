from django.urls import path, include
from .fallback import  callback  
from .login import login


urlpatterns = [
    path('login/', login, name='login'),
    path('callback/', callback, name='callback'),
]