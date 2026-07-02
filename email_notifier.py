import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import config

def send_notification(recipient_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = formataddr(("Campus Lost & Found", config.SENDER_EMAIL))
    msg['To'] = recipient_email

    with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
        server.starttls()
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        server.send_message(msg)