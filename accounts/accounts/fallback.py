from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login
from oauthlib.oauth2 import WebApplicationClient
import requests
import json


from django.contrib.auth.models import User

def get_or_create_user(user_data):
    # Extract the necessary information from the user data
    email = user_data.get('email')
    first_name = user_data.get('given_name')
    last_name = user_data.get('family_name')
    username = email

    # Find or create the user
    user, created = User.objects.get_or_create(username=username, defaults={
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
    })

    # Update user details if necessary
    if not created:
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()

    return user

def callback(request):
    client = WebApplicationClient(settings.AZURE_AD_B2C_CLIENT_ID)
    code = request.GET.get('code')
    token_url, headers, body = client.prepare_token_request(
        f'https://login.microsoftonline.com/{settings.AZURE_AD_B2C_CLIENT_ID}/oauth2/v2.0/token',
        authorization_response=request.build_absolute_uri(),
        redirect_url=settings.AZURE_AD_REDIRECT_URI,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(settings.AZURE_AD_B2C_CLIENT_ID, settings.AZURE_AD_B2C_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = 'https://graph.microsoft.com/oidc/userinfo'
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # User info processing
    user_data = userinfo_response.json()
    user = get_or_create_user(user_data)
    auth_login(request, user)

    return redirect('/')