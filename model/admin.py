from django.contrib import admin
from .archive import Archive
from model.provider import Provider_meta_data_API, Provider_meta_data_FTP, Fetch_history
from mail_service.models import Email_history, Email_notification
from .article import Unreadable_files, Article_attributes, Jsonified_articles

class ArchivedArticleAdmin(admin.ModelAdmin):
    empty_value_display = "N/A"
    # Fields to display 
    list_display = [
                    "provider", "file_content", "unique_key",
                    "file_name_on_source", "file_size", "file_type",
                    "received_on", "processed_on",
                    "status"
                    ]
    # Fields to filter by in the admin interface
    list_filter = ('provider','received_on', 'processed_on', 'status')


class ProviderMetaDataAPIAdmin(admin.ModelAdmin):
    empty_value_display = "N/A"
    list_display = [
                    "api_meta_type", "provider", "base_url",
                    "identifier_code", "identifier_type",
                    "is_token_required",
                    ]
    # Fields to filter by in the admin interface
    list_filter = ('api_meta_type', 'provider', 'identifier_code', 'identifier_type')


class ProviderMetaDataFTPAdmin(admin.ModelAdmin):
    empty_value_display = "N/A"
    list_display = [
                    "provider", "server", "protocol",
                    "site_path", "account"
                    ]
    list_filter = ("provider", "server", "protocol","site_path", "account")


class FetchHistoryAdmin(admin.ModelAdmin):
    empty_value_display = "N/A"
    list_display = [
                    "provider", "status", "error_message", "timestamp"
                    ]
    list_filter = ("provider", "status", "error_message")


class EmailHistoryAdmin(admin.ModelAdmin):
    empty_value_display = "N/A"
    list_display = [
                    "email_ref", "email_subject", "email_body", "status"
                    ]
    list_filter = ("email_ref", "email_subject", "email_body", "status")

class EmailNotification(admin.ModelAdmin):
    empty_value_display = "N/A"
    list_display = [
                    "email_from", "email_to", "email_subject", "email_body"
                    ]
    list_filter = ("email_from", "email_to", "email_subject", "email_body")


class ArticleAdmin(admin.ModelAdmin):
    empty_value_display = "N/A"
    list_display = [
                    "article_file", "journal", "title", 
                    "type_of_record", 
                    "last_step", "last_status",
                    ]
    list_filter = ("article_file", "journal", "title","type_of_record","last_step", "last_status",)


class JsonifiedAdmin(admin.ModelAdmin):
    empty_value_display = "N/A"
    list_display = [
                    "article_file", "journal", "title", 
                    "type_of_record", "article_attributes", 
                    "last_step", "last_status",
                    ]

class UnreadableFilesAdmin(admin.ModelAdmin):
    empty_value_display = "N/A"
    list_display = [
                    "source", "error_msg",
                    "date_stamp"
                    ]


admin.site.register(Archive, ArchivedArticleAdmin)

admin.site.register(Provider_meta_data_API, ProviderMetaDataAPIAdmin)
admin.site.register(Provider_meta_data_FTP, ProviderMetaDataFTPAdmin)
admin.site.register(Fetch_history,  FetchHistoryAdmin)

# admin.site.register(Email_history, EmailHistoryAdmin)
# admin.site.register(Email_notification, EmailNotification)

admin.site.register(Article_attributes, ArticleAdmin)
admin.site.register(Jsonified_articles, JsonifiedAdmin)
admin.site.register(Unreadable_files, UnreadableFilesAdmin)