from fastapi import FastAPI
import requests
from requests.auth import HTTPBasicAuth

app = FastAPI()

API_KEY = "你的API_KEY"

@app.get("/search")
def search_company(name: str):

    url = f"https://api.company-information.service.gov.uk/search/companies?q={name}"

    r = requests.get(url, auth=HTTPBasicAuth(API_KEY, ""))
    data = r.json()

    results = []

    for item in data.get("items", [])[:5]:
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