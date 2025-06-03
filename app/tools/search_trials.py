import requests
import urllib.parse

# BASE_URL = "https://classic.clinicaltrials.gov/api/query/study_fields"

def search_clinical_trials_v2(condition, location=None, status=None, max_results=5):
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    
    params = {
        "format": "json",
        "pageSize": max_results,
        "fields": "protocolSection",  # includes title, status, etc.
        "query.cond": condition
    }

    if location:
        params["query.locn"] = location
    if status:
        params["filter.overallStatus"] = status

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json().get("studies", [])
    except requests.RequestException as e:
        print("❌ API Error:", e)
        return []