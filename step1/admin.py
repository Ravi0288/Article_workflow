from django.contrib import admin
from .archive_article import Archived_article
from .providers import Provider_meta_data_API, Provider_meta_data_FTP, Fetch_history
from .email_notification import Email_history, Email_notification

class ArchivedArticleAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ["provider", "file_content", "unique_key",
                    "file_name_on_source", "file_size", "file_type",
                    "unzipped_folder_size", "received_on", "processed_on",
                    "status", "notes"
                    ]


class ProviderMetaDataAPIAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ["api_meta_type", "provider", "base_url",
                    "identifier_code", "identifier_type", "last_pull_time",
                    "is_token_required", "minimum_delivery_fq", "last_pull_status",
                    "last_error_message"
                    ]

class ProviderMetaDataFTPAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ["provider", "server", "protocol",
                    "site_path", "account", "minimum_delivery_fq",
                    "last_pull_status", "last_error_message", "next_due_date"
                    ]

class FetchHistoryAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ["provider", "status", "error_message", "timestamp"]

class EmailHistoryAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ["email_ref", "email_subject", "email_body", "status"]

class EmailNotificationEmailNotification(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ["applicable_to", "email_from", "email_to", "email_subject", "email_body"]



admin.site.register(Archived_article, ArchivedArticleAdmin)

admin.site.register(Provider_meta_data_API, ProviderMetaDataAPIAdmin)
admin.site.register(Provider_meta_data_FTP, ProviderMetaDataFTPAdmin)
admin.site.register(Fetch_history,  FetchHistoryAdmin)

admin.site.register(Email_history, EmailHistoryAdmin)
admin.site.register(Email_notification, EmailNotificationEmailNotification)