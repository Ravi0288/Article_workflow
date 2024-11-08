from django.shortcuts import redirect
from oauthlib.oauth2 import WebApplicationClient
from django.conf import settings

from django.conf import settings
from django.shortcuts import redirect
from oauthlib.oauth2 import WebApplicationClient


def entra_login(request):
    client = WebApplicationClient(settings.AZURE_AD_B2C_CLIENT_ID)
    auth_url = client.prepare_request_uri(
        f'https://login.microsoftonline.com/{settings.AZURE_AD_B2C_CLIENT_ID}/oauth2/v2.0/authorize',
        redirect_uri=settings.AZURE_AD_B2C_REDIRECT_URI,
        scope=['openid', 'profile'],
    )
    return redirect(auth_url)
