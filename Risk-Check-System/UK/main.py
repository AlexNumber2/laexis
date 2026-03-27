from fastapi import FastAPI
import requests
from requests.auth import HTTPBasicAuth
import base64

app = FastAPI()

API_KEY = "260211e3-ca92-4a9b-a3b6-7fd5b25f3b27"

@app.get("/search")
def search_company(name: str):

    search_url = "https://api.company-information.service.gov.uk/search/companies"

    params = {
        "q": name
    }


    credentials = base64.b64encode(f"{API_KEY}:".encode()).decode()

    headers = {
        "Authorization": f"Basic {credentials}"
    }

    r = requests.get(search_url, params=params, headers=headers)

    print("STATUS:", r.status_code)
    print("RAW:", r.text)   # 👈 关键

    data = r.json()

    items = data.get("items")

    print("ITEMS:", items)  # 👈 关键

    if not items:
        return {"error": "No results", "raw": data}

    results = []

    for item in items[:5]:
        company_number = item["company_number"]

        detail_url = f"https://api.company-information.service.gov.uk/company/{company_number}"
        d = requests.get(detail_url, auth=HTTPBasicAuth(API_KEY, "")).json()

        status = d.get("company_status")

        if status in ["liquidation", "administration"]:
            risk = "HIGH"
        elif status == "dissolved":
            risk = "MEDIUM"
        else:
            risk = "LOW"

        results.append({
            "name": item["title"],
            "status": status,
            "risk": risk
        })

    return results