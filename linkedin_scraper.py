import requests
import os

# Get the SerpAPI key from GitHub Actions secret
api_key = os.getenv("SERPAPI_KEY")

params = {
    "engine": "google_jobs",
    "q": "internship",
    "location": "India",  # You can change this
    "hl": "en",
    "api_key": api_key
}

response = requests.get("https://serpapi.com/search", params=params)
results = response.json()

print("🔍 Latest Internship Listings:\n")

for job in results.get("jobs_results", [])[:5]:
    print(f"🔹 {job['title']} at {job['company_name']}")
    print(f"📍 {job['location']}")
    print(f"🕓 Posted: {job.get('detected_extensions', {}).get('posted_at', 'Unknown')}")
    print(f"👉 Link: {job.get('job_google_link') or job.get('link', 'N/A')}")
    print()
