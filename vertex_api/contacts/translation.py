from modeltranslation.translator import translator, TranslationOptions
from .models import OrganizationDepartment, ContactGroup


class NameAndDescriptionTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


translator.register(OrganizationDepartment, NameAndDescriptionTranslationOptions)
translator.register(ContactGroup, NameAndDescriptionTranslationOptions)
