import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dagster import run_failure_sensor, RunFailureSensorContext, DefaultSensorStatus

# ==============================================================================
# 1. Email Configuration (REPLACE WITH YOUR DATA)
# ==============================================================================
# Your Gmail address that will send the alert
GMAIL_USER = "amrmashaly935@gmail.com"

# Your 16-character App Password (WITHOUT SPACES)
# Example: "dgypwxypokzvqfcc"
GMAIL_APP_PASSWORD = "*************" 

# The recipient email (can be the same as sender)
TO_EMAIL = "amrmashaly935@gmail.com"

# ==============================================================================
# 2. Helper Function: Send Email via SMTP
# ==============================================================================
def send_gmail_alert(subject, body):
    """
    Connects to Gmail SMTP server and sends an email.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail Server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Secure the connection
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(GMAIL_USER, TO_EMAIL, text)
        server.quit()
        
        print(f"✅ Email Alert sent successfully to {TO_EMAIL}")
        
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")

# ==============================================================================
# 3. The Dagster Failure Sensor
# ==============================================================================
@run_failure_sensor(name="email_on_failure", default_status=DefaultSensorStatus.RUNNING)
def email_failure_sensor(context: RunFailureSensorContext):
    """
    Triggered automatically when any job in the pipeline fails.
    """
    # 1. Extract failure details from context
    job_name = context.dagster_run.job_name
    run_id = context.dagster_run.run_id
    error_message = str(context.failure_event.message)
    
    # 2. Prepare Email Content
    subject = f"🚨 Dagster Alert: Job '{job_name}' Failed!"
    body = f"""
    Hello Engineer,
    
    A critical failure occurred in your pipeline execution.
    
    --------------------------------------------------
    🔴 Job Name: {job_name}
    🆔 Run ID:   {run_id}
    --------------------------------------------------
    
    📝 Error Details:
    {error_message}
    
    Please check the Dagster UI for logs.
    """
    
    # 3. Call the helper function to send the alert
    send_gmail_alert(subject, body)