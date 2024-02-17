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
    "order_reference": "0033",
    "customer_code": 49901,
    "invoice_address": {
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
    },
    "delivery_address": {
        "name": "Test Customer Delivery",
        "address_line_1": "Test address 3",
        "address_line_2": "test address 4",
        "city": "Test City",
        "state": "Test State",
        "zip": 21490,
        "country": "United States",
        "email": "test2@gmail.com",
        "phone": 2093784390392,
        "mobile": 2928398239933,
    },
    "payment_method_code": "zion",
    "processor_id": "zion",
    "shipping_cost": "100",
    "warehouse_code": "USLIVEWAREHOUSE",
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
            "discount_percentage": 5,
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
            "discount_percentage": 0,
            "taxes": False,
        },
    ],
}

response = requests.post(
    f"{BASE_URL}/api/process_odoo_sale_order",
    data=json.dumps(so_payload),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token_data['access_token']}"},
)
print(response.json())
