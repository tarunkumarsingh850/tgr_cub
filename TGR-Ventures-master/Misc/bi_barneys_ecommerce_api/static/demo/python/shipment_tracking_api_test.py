import requests
import json

BASE_URL = "http://localhost:9015"

so_payload = {"order_number": "S00132"}

response = requests.get(
    f"{BASE_URL}/api/barney_shipment_track", data=json.dumps(so_payload), headers={"Content-Type": "application/json"}
)
print(response.text)
