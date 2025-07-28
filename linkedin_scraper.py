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

# Debug: Check if email password is loaded
print("🔒 Email password loaded:", bool(email_password))

# Base search parameters
base_params = {
    "engine": "google_jobs",
    "q": "(summer internship OR internship) AND (machine learning OR artificial intelligence OR data science OR software engineer OR software engineering OR computer)",
    "location": "United States",
    "hl": "en",
    "api_key": api_key
}

# Fetch results from two pages (0–9, 10–19)
all_jobs = []
for start in [0, 10]:
    params = base_params.copy()
    params["start"] = start
    response = requests.get("https://serpapi.com/search", params=params)
    results = response.json()
    all_jobs.extend(results.get("jobs_results", []))
    print("🧮 Total internships fetched:", len(all_jobs))


# Format the email body
message_body = "🔍 Latest Internship Listings:\n\n"
for job in all_jobs[:20]:  # Safety cap
    message_body += f"🔹 {job['title']} at {job['company_name']}\n"
    message_body += f"📍 {job['location']}\n"
    message_body += f"🕓 Posted: {job.get('detected_extensions', {}).get('posted_at', 'Unknown')}\n"
    message_body += f"👉 Link: {job.get('job_google_link') or job.get('link', 'N/A')}\n\n"

# Create the email
msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = "📰 Latest Internship Listings (GitHub Actions)"
msg.attach(MIMEText(message_body, "plain"))

# Send email via Gmail SMTP
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    print("✅ Email sent successfully.")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
