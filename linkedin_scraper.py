import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Get secrets from environment
api_key = os.getenv("SERPAPI_KEY")
email_password = os.getenv("EMAIL_APP_KEY")
sender_email = "sarveshhalbe@gmail.com"
receiver_email = "sarveshhalbe@gmail.com"

print("🔒 Email password loaded:", bool(email_password))

base_params = {
    "engine": "google_jobs",
    "q": "internship and computer",
    "location": "USA OR United States OR America",
    "hl": "en",
    "api_key": api_key
}

all_jobs = []
params = base_params.copy()
next_page_token = None
max_pages = 5
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
        print(f"❌ Request failed: {e}")
        break

    print("Full API response:")
    print(results)

    jobs = results.get("jobs_results", [])
    all_jobs.extend(jobs)
    print("🧮 Total internships fetched:", len(all_jobs))

    next_page_token = results.get("next_page_token")

    pages_fetched += 1
    if not next_page_token:
        print("No more pages. Stopping.")
        break
    if pages_fetched >= max_pages:
        print(f"Reached max pages limit ({max_pages}). Stopping.")
        break

# Format email body
message_body = "🔍 Latest Internship Listings:\n\n"
for job in all_jobs[:20]:  # Safety cap to 20 jobs
    message_body += f"🔹 {job.get('title', 'N/A')} at {job.get('company_name', 'N/A')}\n"
    message_body += f"📍 {job.get('location', 'N/A')}\n"
    message_body += f"🕓 Posted: {job.get('detected_extensions', {}).get('posted_at', 'Unknown')}\n"
    message_body += f"👉 Link: {job.get('job_google_link') or job.get('link', 'N/A')}\n\n"

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = "📰 Latest Internship Listings (GitHub Actions)"
msg.attach(MIMEText(message_body, "plain"))

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    print("✅ Email sent successfully.")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
