from django.contrib import admin

from .models import EmailTemplate
from modeltranslation.admin import TabbedTranslationAdmin


class EmailTemplateAdmin(TabbedTranslationAdmin):
    pass


admin.site.register(EmailTemplate, EmailTemplateAdmin)
