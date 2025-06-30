from django.contrib import admin
from .archive import Archive
from model.provider import Providers, Provider_meta_data_API, Provider_meta_data_FTP, Fetch_history, Provider_meta_data_deposit
from model.journal import Journal
from .article import Unreadable_files, Article

class JournalAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = [
                    "journal_title", "publisher", "issn", "collection_status",
                    "harvest_source", "nal_journal_id", "mmsid", "last_updated", "note",
                    "subject_cluster", "requirement_override", "doi"
                    ]
    list_filter = ('publisher', 'collection_status', 'harvest_source', 'note')
    list_per_page = 20
    search_fields = ('issn', 'journal_title', 'nal_journal_id', 'mmsid', 'harvest_source')
   

class ArchivedArticleAdmin(admin.ModelAdmin):
    empty_value_display = 'N/A'
    # Fields to display 
    list_display = [
                    'provider', 'file_content', 'unique_key',
                    'file_name_on_source', 'file_size', 'file_type',
                    'received_on', 'processed_on',
                    'status'
                    ]
    # Fields to filter by in the admin interface
    list_filter = ('provider','received_on', 'processed_on', 'status')
    list_per_page = 20
    search_fields = ('provider__working_name','status','file_name_on_source')


class ProviderAdmin(admin.ModelAdmin):
    empty_value_display = 'N/A'
    list_display = [
                    'official_name', 'working_name', 'in_production',
                    'provider_type', 'source_schema','usda_source'
                    ]
    list_filter = ('official_name', 'in_production', 'provider_type','source_schema', 'usda_source')
    list_per_page = 20
    search_fields = ('official_name',)



class ProviderMetaDataAPIAdmin(admin.ModelAdmin):
    empty_value_display = 'N/A'
    list_display = [
                    'api_meta_type', 'provider', 'base_url',
                    'identifier_code', 'identifier_type',
                    'is_token_required',
                    ]
    # Fields to filter by in the admin interface
    list_filter = ('api_meta_type', 'provider', 'identifier_code', 'identifier_type')
    list_per_page = 20
    search_fields = ('api_meta_type','identifier_code')


class ProviderMetaDataDepositAdmin(admin.ModelAdmin):
    empty_value_display = 'N/A'
    list_display = [
                    'source', 'provider'
                    ]
    # Fields to filter by in the admin interface
    list_filter = ('source', 'provider')
    list_per_page = 20
    search_fields = ('source',)


class ProviderMetaDataFTPAdmin(admin.ModelAdmin):
    empty_value_display = 'N/A'
    list_display = [
                    'provider', 'server', 'protocol',
                    'site_path', 'account'
                    ]
    list_filter = ('provider', 'server', 'protocol','site_path', 'account')
    list_per_page = 20
    search_fields = ('provider__working_name',)



class FetchHistoryAdmin(admin.ModelAdmin):
    empty_value_display = 'N/A'
    list_display = [
                    'provider', 'status', 'error_message', 'timestamp'
                    ]
    list_filter = ('provider', 'status', 'error_message')



class EmailHistoryAdmin(admin.ModelAdmin):
    empty_value_display = 'N/A'
    list_display = [
                    'email_ref', 'email_subject', 'email_body', 'status'
                    ]
    list_filter = ('email_ref', 'email_subject', 'email_body', 'status')


class EmailNotification(admin.ModelAdmin):
    empty_value_display = 'N/A'
    list_display = [
                    'email_from', 'email_to', 'email_subject', 'email_body'
                    ]
    list_filter = ('email_from', 'email_to', 'email_subject', 'email_body')


class ArticleAdmin(admin.ModelAdmin):
    empty_value_display = 'N/A'
    list_display = [
                    'article_file', 'title', 
                    'type_of_record', 
                    'last_step', 'last_status',
                    ]
    list_filter = ('article_file', 'title','type_of_record','last_step', 'last_status')
    list_per_page = 20
    search_fields = ('article_file', 'title','type_of_record')


class UnreadableFilesAdmin(admin.ModelAdmin):
    empty_value_display = 'N/A'
    list_display = [
                    'source', 'error_msg',
                    'date_stamp'
                    ]


admin.site.register(Journal, JournalAdmin)
admin.site.register(Archive, ArchivedArticleAdmin)

admin.site.register(Provider_meta_data_API, ProviderMetaDataAPIAdmin)
admin.site.register(Provider_meta_data_FTP, ProviderMetaDataFTPAdmin)
admin.site.register(Provider_meta_data_deposit, ProviderMetaDataDepositAdmin)
admin.site.register(Providers, ProviderAdmin)
admin.site.register(Fetch_history, FetchHistoryAdmin)

admin.site.register(Article, ArticleAdmin)
admin.site.register(Unreadable_files, UnreadableFilesAdmin)