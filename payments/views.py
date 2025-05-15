import json
from datetime import datetime
import base64
import requests
from django.http import JsonResponse  
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .utils import get_access_token

@csrf_exempt
def lipa_na_mpesa(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    print("Raw request body:", request.body)
    
    try:
        # Parse JSON
        body_str = request.body.decode('utf-8')
        print("Decoded body:", body_str)
        
        data = json.loads(body_str)
        print("Parsed data:", data)
        
        phone = data.get("phone")
        amount = data.get("amount")
        account_ref = data.get("account_reference", "TestAccount")
        description = data.get("description", "Payment")
        
        if not phone or not amount:
            return JsonResponse({'error': 'Phone and amount are required'}, status=400)
        
        try:
            access_token = get_access_token()
            print("Access token obtained:", access_token)
        except Exception as e:
            return JsonResponse({'error': f'Failed to get access token: {str(e)}'}, status=400)
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((settings.DARAJA_SHORTCODE + settings.DARAJA_PASSKEY + timestamp).encode()).decode()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": settings.DARAJA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": 174379,
            "PhoneNumber": phone,
            "CallBackURL": "https://mydomain.com/api/callback/",
            "AccountReference": account_ref,
            "TransactionDesc": description
        }
        
        print("Sending payload to M-Pesa API:", payload)
        
        try:
            response = requests.post(
                f"{settings.DARAJA_BASE_URL}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers=headers
            )
            
            print("M-Pesa API response status:", response.status_code)
            print("M-Pesa API response content:", response.text)
            
            if response.status_code >= 400:
                return JsonResponse({
                    'error': 'M-Pesa API error',
                    'status_code': response.status_code,
                    'response': response.text
                }, status=400)
                
            return JsonResponse(response.json())
        except requests.RequestException as e:
            return JsonResponse({'error': f'Error connecting to M-Pesa API: {str(e)}'}, status=400)
    
    except json.JSONDecodeError as e:
        return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)