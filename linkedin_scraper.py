import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Get secrets from environment
api_key = os.getenv("SERPAPI_KEY")
email_password = os.getenv("EMAIL_APP_PASSWORD")
sender_email = "sarveshhalbe@gmail.com"
receiver_email = "sarveshhalbe@gmail.com"

# Fetch internships from SerpAPI
params = {
    "engine": "google_jobs",
    "q": "internship",
    "location": "India",
    "hl": "en",
    "api_key": api_key
}

response = requests.get("https://serpapi.com/search", params=params)
results = response.json()

# Format results
message_body = "🔍 Latest Internship Listings:\n\n"
for job in results.get("jobs_results", [])[:5]:
    message_body += f"🔹 {job['title']} at {job['company_name']}\n"
    message_body += f"📍 {job['location']}\n"
    message_body += f"🕓 Posted: {job.get('detected_extensions', {}).get('posted_at', 'Unknown')}\n"
    message_body += f"👉 Link: {job.get('job_google_link') or job.get('link', 'N/A')}\n\n"

# Create email message
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
