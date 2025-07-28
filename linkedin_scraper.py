import requests
import os

api_key = os.getenv("SERPAPI_KEY")

base_params = {
    "engine": "google_jobs",
    "q": "internship",
    "location": "India",
    "hl": "en",
    "api_key": api_key
}

all_jobs = []
params = base_params.copy()
next_page_token = None

while True:
    if next_page_token:
        params["next_page_token"] = next_page_token
    else:
        params.pop("next_page_token", None)

    response = requests.get("https://serpapi.com/search", params=params)
    results = response.json()

    # Debug output
    print("Full API response:")
    print(results)

    jobs = results.get("jobs_results", [])
    all_jobs.extend(jobs)
    print("🧮 Total internships fetched:", len(all_jobs))

    # Check if there is a next page token
