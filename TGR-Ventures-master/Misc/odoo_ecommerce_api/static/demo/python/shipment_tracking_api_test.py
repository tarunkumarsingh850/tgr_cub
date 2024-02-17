import requests
import json

BASE_URL = "http://192.168.10.22:9015"

payload = {
    "client_id": "OpWNZEQ9MlY8wfXdJnJsRNfFP432Zo",
    "client_secret": "tgPaj5jqLRm4odYeE9F1l6PsWne2Br",
    "grant_type": "client_credentials",
}

response = requests.post(f"{BASE_URL}/oauth2/access_token", data=payload, headers={"Accept": "*/*"})
token_data = json.loads(response.text)

so_payload = {"order_number": "SSUK-00051126"}

response = requests.post(
    f"{BASE_URL}/api/dropship_shipment_track",
    data=json.dumps(so_payload),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token_data['access_token']}"},
)
print(response.text)
