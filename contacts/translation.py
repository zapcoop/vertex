from modeltranslation.translator import translator, TranslationOptions
from .models import OrganizationDepartment

class OrganizationDepartmentTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


translator.register(OrganizationDepartment, OrganizationDepartmentTranslationOptions)
