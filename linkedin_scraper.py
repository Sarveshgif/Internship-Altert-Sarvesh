import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict
from datetime import datetime
import re

# Helper: categorize posting time
def categorize_posted_time(posted_str):
    """
    Categorizes posting time into: 'Today', 'Yesterday', '2 days ago', '3 days ago', or None (older).
    """
    if not posted_str:
        return None
    posted_str = posted_str.lower()
    if any(kw in posted_str for kw in ["just posted", "today", "hour", "minute"]):
        return "Today"
    match = re.search(r"(\d+)\s+day", posted_str)
    if match:
        days = int(match.group(1))
        if days == 1:
            return "Yesterday"
        elif days == 2:
            return "2 days ago"
        elif days == 3:
            return "3 days ago"
    return None

# Secrets from environment
api_key = os.getenv("SERPAPI_KEY")
email_password = os.getenv("EMAIL_APP_KEY")
sender_email = "sarveshhalbe@gmail.com"
receiver_email = "sarveshhalbe@gmail.com"

print("🔐 Email password loaded:", bool(email_password))

locations = ["USA", "United States", "America"]
all_jobs = []
max_pages = 5

# Fetch jobs
for loc in locations:
    print(f"🌍 Searching internships in: {loc}")
    base_params = {
        "engine": "google_jobs",
        "q": "internship and computer",
        "location": loc,
        "hl": "en",
        "api_key": api_key
    }
    params = base_params.copy()
    next_page_token = None
    pages_fetched = 0

    while True:
        if next_page_token:
            params["next_page_token"] = next_page_token
        else:
            params.pop("next_page_token", None)

        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            response.raise_for_status()
            results = response.json()
        except Exception as e:
            print(f"❌ Error fetching for {loc}: {e}")
            break

        jobs = results.get("jobs_results", [])
        all_jobs.extend(jobs)
        print(f"📥 Total fetched so far: {len(all_jobs)}")

        next_page_token = results.get("next_page_token")
        pages_fetched += 1

        if not next_page_token or pages_fetched >= max_pages:
            break

# Group by posting time
categorized_jobs = defaultdict(list)
for job in all_jobs:
    posted_at = job.get('detected_extensions', {}).get('posted_at', '')
    category = categorize_posted_time(posted_at)
    if category:
        categorized_jobs[category].append(job)

# Print summary
print("📊 Jobs by day:")
for day in ["Today", "Yesterday", "2 days ago", "3 days ago"]:
    print(f"➡️ {day}: {len(categorized_jobs[day])} jobs")

# Build email body
message_body = f"🗓️ Internship Digest — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
message_body += "🔍 Showing internships posted in the last 3 days:\n\n"

for day in ["Today", "Yesterday", "2 days ago", "3 days ago"]:
    jobs = categorized_jobs.get(day, [])
    if not jobs:
        continue
    message_body += f"📅 {day} ({len(jobs)} jobs):\n"
    for job in jobs[:10]:  # Max 10 per category
        title = job.get('title', 'N/A')
        company = job.get('company_name', 'N/A')
        location = job.get('location', 'N/A')
        posted_at = job.get('detected_extensions', {}).get('posted_at', 'Unknown')
        link = job.get('job_google_link') or job.get('link', 'N/A')

        message_body += f"🔹 {title} at {company}\n"
        message_body += f"📍 {location} | 🕓 {posted_at}\n"
        message_body += f"👉 {link}\n\n"
    message_body += "\n"

# Email setup
msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = "📰 Internship Listings (Last 3 Days)"
msg.attach(MIMEText(message_body, "plain"))

# Send the email
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    print("✅ Email sent successfully.")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
