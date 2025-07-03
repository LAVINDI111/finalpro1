"""
Notification Service for ACNSMS
Handles email and SMS notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

class NotificationService:
    """Service class for handling notifications"""
    
    def __init__(self):
        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        # Twilio configuration for SMS
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        # Initialize Twilio client
        if self.twilio_account_sid and self.twilio_auth_token:
            self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        else:
            self.twilio_client = None
            print("Warning: Twilio credentials not found. SMS functionality disabled.")
    
    def send_email(self, to_email, subject, message):
        """
        Send email notification
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            message (str): Email message body
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach message body
            msg.attach(MIMEText(message, 'plain'))
            
            # Connect to server and send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable TLS encryption
            server.login(self.email_user, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_user, to_email, text)
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_sms(self, to_phone, message):
        """
        Send SMS notification
        
        Args:
            to_phone (str): Recipient phone number (with country code)
            message (str): SMS message body
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.twilio_client:
                print("SMS service not configured")
                return False
            
            # Send SMS using Twilio
            message = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=to_phone
            )
            
            print(f"SMS sent successfully to {to_phone}. Message SID: {message.sid}")
            return True
            
        except Exception as e:
            print(f"Failed to send SMS to {to_phone}: {str(e)}")
            return False
    
    def send_bulk_email(self, recipients, subject, message):
        """
        Send email to multiple recipients
        
        Args:
            recipients (list): List of email addresses
            subject (str): Email subject
            message (str): Email message body
        
        Returns:
            dict: Results with success/failure counts
        """
        results = {'success': 0, 'failed': 0, 'errors': []}
        
        for email in recipients:
            if self.send_email(email, subject, message):
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"Failed to send to {email}")
        
        return results
    
    def send_bulk_sms(self, recipients, message):
        """
        Send SMS to multiple recipients
        
        Args:
            recipients (list): List of phone numbers
            message (str): SMS message body
        
        Returns:
            dict: Results with success/failure counts
        """
        results = {'success': 0, 'failed': 0, 'errors': []}
        
        for phone in recipients:
            if self.send_sms(phone, message):
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"Failed to send to {phone}")
        
        return results