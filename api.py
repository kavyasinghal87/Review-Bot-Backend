from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Try to import your logic
try:
    from main import auditor_chain, get_optimized_code
except ImportError as e:
    print(f"CRITICAL ERROR: Could not find functions in main.py: {e}")
    sys.exit(1)

app = FastAPI()

# Enable CORS for the website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Email Configuration ---
# Tip: It's better to put these in Render Environment Variables later
GMAIL_USER = "your_email@gmail.com"  # Your Gmail address
GMAIL_APP_PASS = "your_16_char_app_password"  # The 16-character code from Google
RECEIVER_EMAIL = "your_email@gmail.com"  # Where you want to receive the alerts

def send_visitor_email(name, email):
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = f"🚀 New ReviewBot Visitor: {name}"

        body = f"A user has logged into ReviewBot AI.\n\nDetails:\nName: {name}\nEmail: {email}"
        msg.attach(MIMEText(body, 'plain'))

        # Standard Gmail SMTP settings
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASS)
        server.sendmail(GMAIL_USER, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

class LoginRequest(BaseModel):
    name: str
    email: str

class CodeRequest(BaseModel):
    code: str

# --- Updated Registration Endpoint ---
@app.post("/register")
async def register_visitor(request: LoginRequest):
    # This sends the email to you immediately
    email_sent = send_visitor_email(request.name, request.email)
    
    if email_sent:
        return {"status": "SUCCESS"}
    else:
        # We return SUCCESS so the user can still enter, but log the error on the server
        print("ALERT: Visitor logged in but email notification failed.")
        return {"status": "SUCCESS"}

@app.post("/audit")
async def audit_code(request: CodeRequest):
    try:
        result = auditor_chain.invoke({"code": request.code})
        return result
    except Exception as e:
        return {"status": "ERROR", "errors": [str(e)]}

@app.post("/optimize")
async def optimize_code(request: CodeRequest):
    try:
        faster_code = get_optimized_code(request.code)
        return {"optimized_code": faster_code}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    # Bind to 0.0.0.0 for Render production
    uvicorn.run(app, host="0.0.0.0", port=port)