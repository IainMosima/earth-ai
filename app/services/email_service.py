import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.sender_email = os.getenv('EMAIL_FROM')
    
    async def send_signed_urls_email(self, email: str, urls: dict) -> None:
        """
        Sends an email with signed URLs for photo uploads
        
        Args:
            email: User's email address
            urls: Dictionary containing signed URLs
        """
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = email
        message['Subject'] = 'Complete Your Earth AI Registration'
        
        email_content = f"""
        <h1>Complete Your Earth AI Registration</h1>
        <p>Thank you for starting your registration with Earth AI. To complete the process, please upload the required photos using the links below:</p>
        
        <h2>Upload Instructions:</h2>
        <p>1. <a href="{urls['ground_photo_url']}">Click here to upload your ground photo</a> (Valid for 1 hour)</p>
        <p>2. <a href="{urls['aerial_photo_url']}">Click here to upload your aerial photo</a> (Valid for 1 hour)</p>
        
        <p>After successfully uploading both photos, you will receive a confirmation email with your account details.</p>
        
        <p>Thank you,<br>
        The Earth AI Team</p>
        """
        
        message.attach(MIMEText(email_content, 'html'))
        
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(message)
    
    async def send_registration_completion_email(self, email: str) -> None:
        """
        Sends a registration completion confirmation email
        
        Args:
            email: User's email address
        """
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = email
        message['Subject'] = 'Earth AI Registration Complete'
        
        email_content = f"""
        <h1>Registration Complete</h1>
        <p>Congratulations! Your Earth AI registration is now complete.</p>
        <p>You can now log in to your account and start using our services.</p>
        
        <p>Thank you,<br>
        The Earth AI Team</p>
        """
        
        message.attach(MIMEText(email_content, 'html'))
        
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(message)

email_service = EmailService()
