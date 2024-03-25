from django.contrib import admin
from .archive_article import Archived_article_attribute


# Register your models here.

@admin.register(Archived_article_attribute)
class Archived_article_attribute_admin(admin.ModelAdmin):
    # fields = ["name", "title"]
    # exclude = ["birth_date"]
    pass

# admin.site.register(Archived_artical_attribute, Archived_artical_attribute_admin)