from django.contrib import admin
from contacts.models import (
    ContactGroup,
    OrganizationDepartment,
    EmailAddress,
    PhoneNumber,
    URL,
    Organization,
    OrganizationAlias,
    Person,
    PeopleOrganizations,
    Place
)


class PeopleOrganizationsInline(admin.StackedInline):
    model = PeopleOrganizations
    extra = 0


class PersonAdmin(admin.ModelAdmin):
    model = Person

    inlines = (PeopleOrganizationsInline,)


admin.site.register(ContactGroup)
admin.site.register(OrganizationDepartment)
admin.site.register(EmailAddress)
admin.site.register(PhoneNumber)
admin.site.register(Place)
admin.site.register(URL)
admin.site.register(Organization)
admin.site.register(OrganizationAlias)
admin.site.register(Person, PersonAdmin)
