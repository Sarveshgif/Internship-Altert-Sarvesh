import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import re

# ========= CONFIGURATION ===========
SERP_API_KEY = os.getenv("SERPAPI_KEY")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_KEY")
SENDER_EMAIL = "sarveshhalbe@gmail.com"
RECEIVER_EMAIL = "sarveshhalbe@gmail.com"
MAX_RESULTS = 20
SEARCH_QUERY = "internship computer OR software OR programming OR development"
LOCATIONS = ["USA", "United States", "America"]
MAX_PAGES = 5
# ===================================

# Smarter time categorizer
def parse_posted_date(posted_str):
    if not posted_str:
        return None
    posted_str = posted_str.lower().strip()

    if any(kw in posted_str for kw in ["just posted", "today", "hour", "minute"]):
        return datetime.today()
    if "yesterday" in posted_str:
        return datetime.today() - timedelta(days=1)
    match = re.search(r"(\d+)\s+day", posted_str)
    if match:
        return datetime.today() - timedelta(days=int(match.group(1)))

    return None  # fallback

# Fetch jobs from SerpAPI
def fetch_jobs():
    all_jobs = []
    for loc in LOCATIONS:
        print(f"🌎 Fetching jobs for location: {loc}")
        base_params = {
            "engine": "google_jobs",
            "q": SEARCH_QUERY,
            "location": loc,
            "hl": "en",
            "api_key": SERP_API_KEY
        }

        next_page_token = None
        pages_fetched = 0

        while pages_fetched < MAX_PAGES:
            params = base_params.copy()
            if next_page_token:
                params["next_page_token"] = next_page_token

            try:
                response = requests.get("https://serpapi.com/search", params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                print(f"❌ Error fetching jobs: {e}")
                break

            jobs = data.get("jobs_results", [])
            print(f"➕ Found {len(jobs)} jobs in this batch.")
            all_jobs.extend(jobs)

            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break
            pages_fetched += 1

    return all_jobs

# Filter and sort recent jobs
def filter_recent_jobs(jobs):
    parsed_jobs = []
    for job in jobs:
        title = job.get("title", "N/A").strip()
        company = job.get("company_name", "N/A").strip()
        location = job.get("location", "N/A").strip()
        link = job.get("job_google_link") or job.get("link", "N/A")
        posted_raw = job.get("detected_extensions", {}).get("posted_at", '')

        # Try to parse date
        posted_date = parse_posted_date(posted_raw)

        if posted_date:
            parsed_jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "posted": posted_date,
                "posted_raw": posted_raw,
                "link": link
            })

    print(f"📅 {len(parsed_jobs)} jobs with valid posting dates found.")
    # Sort most recent first
    parsed_jobs.sort(key=lambda x: x["posted"], reverse=True)
    return parsed_jobs[:MAX_RESULTS]

# Build email body
def build_email(jobs):
    header = f"🗓️ Internship Digest — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += f"🔍 Top {MAX_RESULTS} most recent internships:\n\n"

    body = ""
    for i, job in enumerate(jobs, 1):
        body += f"{i}. {job['title']} at {job['company']}\n"
        body += f"📍 {job['location']} | 🕓 {job['posted_raw']}\n"
        body += f"🔗 {job['link']}\n\n"

    return header + body

# Send email
def send_email(subject, content):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(content, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Email send failed: {e}")

# ====== MAIN EXECUTION =========
def main():
    if not SERP_API_KEY:
        print("🚫 Missing SerpAPI key.")
        return
    if not EMAIL_PASSWORD:
        print("🚫 Missing email password.")
        return

    jobs_raw = fetch_jobs()
    recent_jobs = filter_recent_jobs(jobs_raw)
    if not recent_jobs:
        print("⚠️ No recent jobs found.")
        return

    email_body = build_email(recent_jobs)
    print("📨 Email preview:\n", email_body[:1000])  # Show preview
    send_email("📰 Top Recent Internships (Filtered)", email_body)

if __name__ == "__main__":
    main()
