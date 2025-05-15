import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

def get_access_token():
    url = f"{settings.DARAJA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(settings.DARAJA_CONSUMER_KEY, settings.DARAJA_CONSUMER_SECRET))
    return response.json().get('access_token')
