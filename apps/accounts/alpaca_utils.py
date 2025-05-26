# alpaca_utils.py
import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from django.db import connection

def create_alpaca_broker_account(email, first_name, last_name, street_address, phone_number, date_of_birth):
    url = "https://broker-api.sandbox.alpaca.markets/v1/accounts"

    auth = HTTPBasicAuth(settings.ALPACA_BROKER_API_KEY, settings.ALPACA_BROKER_SECRET_KEY)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
  "contact": {
    "email_address": email,
    "phone_number": f"+1{phone_number}",
    "street_address": [street_address],
    "unit": "et mag",
    "city": "San Mateo",
    "state": "CA",
    "postal_code": "94401"
  },
  "identity": {
    "given_name": first_name,
    "family_name": last_name,
    "date_of_birth": date_of_birth,
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
    "given_name": "Jane",
    "family_name": "Doe",
    "email_address": "x@gmail.com"
  },
  "enabled_assets": [
    "us_equity"
  ]
}

    print("Enviando solicitud a Alpaca con el siguiente payload:")
    print(payload)

    response = requests.post(url, json=payload, headers=headers, auth=auth)

    print("Respuesta de Alpaca:")
    print(f"Status Code: {response.status_code}")
    print(response.text)

    if response.status_code == 200:
        data = response.json()
        kyc_status = data.get("identity_verification", {}).get("status", "pendiente")
        alpaca_id = data["id"]  
        print("Usuario creado. ID Alpaca:", alpaca_id)

        return {
            "success": True,
            "account_id": data["id"],
            "kyc_status": kyc_status,
            "alpaca_id": alpaca_id
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


def place_market_order(account_id, symbol, qty, side):
    
    url = f"https://broker-api.sandbox.alpaca.markets/v1/trading/accounts/{account_id}/orders"
    auth = HTTPBasicAuth(settings.ALPACA_BROKER_API_KEY, settings.ALPACA_BROKER_SECRET_KEY)
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    payload = {
        "symbol": symbol.upper(),
        "qty": int(qty),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc"
    }

    response = requests.post(url, json=payload, headers=headers, auth=auth)
    if response.status_code != 200:
        return {"error": f"Error al crear orden: {response.text}"}
    
        

    data = response.json()
    order_id = data.get("id")
    status = data.get("status")

    return {
            "data": data,
            "order_id": order_id,
            "status": status
        }


def create_ach(user_id): 
    print("uid: ",user_id)
    ach_url = f"https://broker-api.sandbox.alpaca.markets/v1/accounts/{user_id}/ach_relationships"

    auth = HTTPBasicAuth(settings.ALPACA_BROKER_API_KEY, settings.ALPACA_BROKER_SECRET_KEY)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    ach_data = {
        "account_owner_name": "John Doe",
        "bank_account_type": "CHECKING",
        "bank_account_number": "32131231abc",
        "bank_routing_number": "121000358",
        "nickname": "Bank of America Checking"
    }

    ach_response = requests.post(ach_url, json=ach_data, headers=headers, auth=auth, verify=False)

    if ach_response.status_code in [200, 201]:
        ach_json = ach_response.json()
        ach_id = ach_json.get("id")
        print("ACH ID:", ach_id)
        return ach_id
    else:
        print("Error al crear relación ACH:", ach_response.status_code, ach_response.text)
        return None
    
def transfer(user_id, monto, tr_id): 
    print("uid: ",user_id)
    ach_url = f"https://broker-api.sandbox.alpaca.markets/v1/accounts/{user_id}/transfers"

    auth = HTTPBasicAuth(settings.ALPACA_BROKER_API_KEY, settings.ALPACA_BROKER_SECRET_KEY)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Datos de prueba — deberías usar valores válidos y seguros en producción
    ach_data = {
    "transfer_type": "ach",
    "relationship_id": tr_id,
    "amount": str(monto),
    "direction": "INCOMING"
}

    ach_response = requests.post(ach_url, json=ach_data, headers=headers, auth=auth, verify=False)

    if ach_response.status_code in [200, 201]:
        ach_json = ach_response.json()
        print("Transacción realizada")
        return ach_json
    else:
        print("Error al realizar transacción:", ach_response.status_code, ach_response.text)
        return None
    

def actualizar_saldo(alpaca_id, monto, sumar=False):
    with connection.cursor() as cursor:
        cursor.execute("SELECT saldo FROM usuarios WHERE alpaca_id = %s", [alpaca_id])
        saldo_actual = cursor.fetchone()

        if saldo_actual is None:
            return False, "Usuario no encontrado"

        saldo_actual = saldo_actual[0]
        nuevo_saldo = saldo_actual + monto if sumar else saldo_actual - monto

        if nuevo_saldo < 0:
            return False, "Fondos insuficientes"

        cursor.execute("UPDATE usuarios SET saldo = %s WHERE alpaca_id = %s", [nuevo_saldo, alpaca_id])
        return True, nuevo_saldo

    
def sincronizar_ordenes(alpaca_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT estado FROM ordenes WHERE alpaca_id = %s", (alpaca_id,))
        todos_los_estados = cursor.fetchall()
        print("Estados de órdenes del usuario:", todos_los_estados)

        cursor.execute("SELECT * FROM ordenes WHERE estado IN ('pending', 'pending_new', 'new', 'accepted') AND alpaca_id = %s", (alpaca_id,))
        columnas = [col[0] for col in cursor.description]
        ordenes = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        print("Órdenes que serán sincronizadas:", ordenes)

        for orden in ordenes:
            print("Orden actual:", orden)

            order_id = orden["order_id"]
            alpaca_id = orden["alpaca_id"]
            symbol = orden["symbol"]
        
            print('ssup')

            ach_url = f"https://broker-api.sandbox.alpaca.markets/v1/trading/accounts/{alpaca_id}/orders/{order_id}"

            auth = HTTPBasicAuth(settings.ALPACA_BROKER_API_KEY, settings.ALPACA_BROKER_SECRET_KEY)

            headers = {
                "Accept": "application/json"
            }


            r = requests.get(ach_url, headers=headers, auth=auth)

            print("Status code:", r.status_code)
            print("Response body:", r.text)

            if r.status_code != 200:
                continue

            data = r.json()
            estado = data["status"]
            print('xxxxxxxxxxxx')
            print("sincronizar ordenas mao: ", estado)
            qty_filled = int(data.get("filled_qty") or 0)
            precio_unitario = float(data.get("filled_avg_price") or 0.0)
            total = precio_unitario * qty_filled

            if estado == "filled":
                cursor.execute("""
                    UPDATE ordenes
                    SET estado = %s, precio_unitario = %s, total = %s
                    WHERE order_id = %s
                """, (estado, precio_unitario, total, order_id))
                connection.commit()

                cursor.execute("SELECT id, cantidad FROM portafolio WHERE alpaca_id = %s AND symbol = %s",
                               (alpaca_id, symbol))
                existente = cursor.fetchone()

                if existente:
                    nueva_cantidad = existente[1] + qty_filled
                    cursor.execute("UPDATE portafolio SET cantidad = %s WHERE id = %s", (nueva_cantidad, existente[0]))
                    connection.commit()
                else:
                    cursor.execute("INSERT INTO portafolio (alpaca_id, symbol, cantidad) VALUES (%s, %s, %s)",
                                   (alpaca_id, symbol, qty_filled))
                    
                    connection.commit()
