from django.contrib import admin
from .archive import Archive
from .provider import Provider_meta_data_API, Provider_meta_data_FTP, Fetch_history
from mail_service.models import Email_history, Email_notification

class ArchivedArticleAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ["provider", "file_content", "unique_key",
                    "file_name_on_source", "file_size", "file_type",
                    "received_on", "processed_on",
                    "status"
                    ]


class ProviderMetaDataAPIAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ["api_meta_type", "provider", "base_url",
                    "identifier_code", "identifier_type",
                    "is_token_required",
                    ]

class ProviderMetaDataFTPAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ["provider", "server", "protocol",
                    "site_path", "account"
                    ]

class FetchHistoryAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ["provider", "status", "error_message", "timestamp"]

class EmailHistoryAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ["email_ref", "email_subject", "email_body", "status"]

class EmailNotification(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ["email_from", "email_to", "email_subject", "email_body"]



admin.site.register(Archive, ArchivedArticleAdmin)

admin.site.register(Provider_meta_data_API, ProviderMetaDataAPIAdmin)
admin.site.register(Provider_meta_data_FTP, ProviderMetaDataFTPAdmin)
admin.site.register(Fetch_history,  FetchHistoryAdmin)

admin.site.register(Email_history, EmailHistoryAdmin)
admin.site.register(Email_notification, EmailNotification)