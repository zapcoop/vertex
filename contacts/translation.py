from modeltranslation.translator import translator, TranslationOptions
from .models import ContactGroup, OrganizationDepartment


class ContactGroupTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


class OrganizationDepartmentTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


translator.register(ContactGroup, ContactGroupTranslationOptions)
translator.register(OrganizationDepartment, OrganizationDepartmentTranslationOptions)
