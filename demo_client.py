import requests

BASE = "http://127.0.0.1:8000/api"


print("\n=== ADD TICKETS ===")

resp = requests.post(
    f"{BASE}/tickets/",
    data={
        "title": "Printer not working",
        "description": "Office printer keeps jamming",
        "priority": 3
    },
)
print("\nAdd ticket 1:")
print("Status:", resp.status_code)
ticket1 = resp.json()
print("Response:", ticket1)