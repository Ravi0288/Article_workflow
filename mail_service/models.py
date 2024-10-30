from django.db import models

# model to list all email api wise for email notification purpose. This is master table
class Email_notification(models.Model):
    applicable_to = models.TextField(help_text="Enter any name to indentify where this record will be used as foreign key for sending email")
    email_from = models.TextField(help_text="Enter email address of the sender")
    email_to = models.TextField(help_text="Enter list of email addresses of the receivers in this format email-1;email-2;email3;and so on;")
    email_subject = models.TextField(default='Error occurred',
                                     help_text="Email default subject"
                                     )
    email_body = models.TextField(blank=True, null=True,
                                  help_text="Email body. This will be the error message from the exceptions handlers"
                                  )

    def __str__(self) -> str:
        return self.applicable_to
    


# Email history to maintain log of each email sent.
# Each time email will be sent a new entry will be made to this table with failed of success status
class Email_history(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    email_ref = models.ForeignKey(Email_notification, related_name='email_notification' , on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=10, default='completed')
    email_subject = models.TextField(default='Error occurred')
    email_body = models.TextField(default='Error occurred')

    def __str__(self) -> str:
        return self.email_ref.applicable_to + '->' + self.status

