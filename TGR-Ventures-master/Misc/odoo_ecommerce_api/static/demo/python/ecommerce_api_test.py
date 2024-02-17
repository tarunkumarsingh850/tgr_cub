import requests
import json

BASE_URL = "http://localhost:9015"
# ====================Get access token==========================
payload = {
    "client_id": "M1uKcMQFSNwcJunUMgYaGlChctBUNX",
    "client_secret": "jBkf6MEIUxpFo68LjyD4SVU2AhxjlX",
    "grant_type": "client_credentials",
}

response = requests.post(f"{BASE_URL}/oauth2/access_token", data=payload, headers={"Accept": "*/*"})
token_data = response.json()

# ==================Create sale order============================
so_payload = {
    "company_details": {"code": "FAST0001", "name": "Test Company"},
    "customer_details": {
        "code": "FAST0001",
        "name": "Test Customer",
        "address_line_1": "Test address 1",
        "address_line_2": "test address 2",
        "city": "Test City",
        "state": "Test State",
        "zip": 21490,
        "country": "United States",
        "email": "test@gmail.com",
        "phone": 2093784390392,
        "mobile": 2928398239933,
        "warehouse_code": "USLIVEWAREHOUSE",
    },
    "order_details": [
        {
            "product_details": {
                "code": "FURN_6666",
                "name": "TV",
                "product_type": "consu",
                "sale_price": 50000,
                "product_category": "All",
            },
            "currency": "USD",
            "quantity": 2,
            "unit_price": 50000,
            "taxes": False,
        },
        {
            "product_details": {
                "code": "E-COM11",
                "name": "Drawer",
                "product_type": "consu",
                "sale_price": 50500,
                "product_category": "All",
            },
            "currency": "USD",
            "quantity": 3,
            "unit_price": 50500,
            "taxes": False,
        },
    ],
}

response = requests.post(
    f"{BASE_URL}/api/process_sale_order",
    data=json.dumps(so_payload),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token_data['access_token']}"},
)
print(response.json())
