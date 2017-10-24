from modeltranslation.translator import translator, TranslationOptions

from contacts.models import OrganizationDepartment, ContactGroup, PeopleOrganizations, Person


class NameAndDescriptionTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


class PersonTranslationOptions(TranslationOptions):
    fields = ('title', 'suffix')

class PeopleOrganizationsTranslationOptions(TranslationOptions):
    fields = ('role',)



translator.register(OrganizationDepartment, NameAndDescriptionTranslationOptions)
translator.register(ContactGroup, NameAndDescriptionTranslationOptions)
translator.register(Person, PersonTranslationOptions)
translator.register(PeopleOrganizations, PeopleOrganizationsTranslationOptions)
