import smtplib
from email.message import EmailMessage

# Replace these with appropriate values
EMAIL_SENDER = 'nikhilbabu213@gmail.com'
EMAIL_PASSWORD = 'lcoh vcco vbpe hgtg '
EMAIL_RECEIVER = 'lonigo3077@dariolo.com'

def send_email_alert(subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Email alert sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")