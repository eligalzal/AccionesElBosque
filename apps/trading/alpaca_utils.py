# alpaca_utils.py
import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

def create_alpaca_broker_account(user, email, first_name, last_name):
    url = "https://broker-api.sandbox.alpaca.markets/v1/accounts"

    auth = HTTPBasicAuth(settings.ALPACA_BROKER_API_KEY, settings.ALPACA_BROKER_SECRET_KEY)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
  "contact": {
    "email_address": email,
    "phone_number": "+15556667788",
    "street_address": ["lamatraca"],
    "unit": "et mag",
    "city": "San Mateo",
    "state": "CA",
    "postal_code": "94401"
  },
  "identity": {
    "given_name": "meow",
    "family_name": "Doe",
    "date_of_birth": "1990-01-01",
    "tax_id": "132-56-6739",
    "tax_id_type": "USA_SSN",
    "country_of_citizenship": "AUS",
    "country_of_birth": "AUS",
    "country_of_tax_residence": "USA",
    "funding_source": ["employment_income"]
  },
  "disclosures": {
    "is_control_person": False,
    "is_affiliated_exchange_or_finra": False,
    "is_politically_exposed": False,
    "immediate_family_exposed": False
  },
  "agreements": [
    {
      "agreement": "customer_agreement",
      "signed_at": "2024-01-01T00:00:00Z",
      "ip_address": "192.168.1.1"
    },
    {
      "agreement": "account_agreement",
      "signed_at": "2024-01-01T00:00:00Z",
      "ip_address": "192.168.1.1"
    },
    {
      "agreement": "margin_agreement",
      "signed_at": "2024-01-01T00:00:00Z",
      "ip_address": "192.168.1.1"
    }
  ],
  "documents": [
    {
      "document_type": "identity_verification",
      "document_sub_type": "passport",
      "content": "/9j/Cg==",
      "mime_type": "image/jpeg"
    }
  ],
  "trusted_contact": {
    "given_name": first_name,
    "family_name": last_name,
    "email_address": email
  },
  "enabled_assets": [
    "us_equity"
  ]
}

    print("📤 Enviando solicitud a Alpaca con el siguiente payload:")
    print(payload)

    response = requests.post(url, json=payload, headers=headers, auth=auth)

    print("📥 Respuesta de Alpaca:")
    print(f"Status Code: {response.status_code}")
    print(response.text)

    if response.status_code == 200:
        data = response.json()
        return {
            "success": True,
            "account_id": data["id"],
            "kyc_status": data["identity_verification"]["status"]
        }
    else:
        try:
            error = response.json()
        except ValueError:
            error = response.text
        return {
            "success": False,
            "error": error
        }