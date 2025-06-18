from django.core.mail import EmailMessage
from django.conf import settings
from datetime import datetime

def send_email_notification():

    subject = 'Notification: Step 11 Execution Successful - Alma S3 Upload Complete'

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"""
            This is an automated notification.

            Step 11 of the article processing pipeline has completed successfully.

            All eligible article metadata and digital content have been uploaded to Alma's S3 storage.

            No errors were encountered during execution.

            Timestamp: {timestamp}

            
            --
            System Notification
        """

    # Send email
    email_from = settings.EMAIL_HOST_USER 
    email_to = settings.EMAIL_TO if isinstance(settings.EMAIL_TO, list) else [settings.EMAIL_TO]
    
    msg = EmailMessage(subject, message, email_from, email_to)
    msg.send(fail_silently=True)
