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


class OrganizationAliasesInline(admin.TabularInline):
    model = OrganizationAlias
    extra = 0


class PersonAdmin(admin.ModelAdmin):
    model = Person

    inlines = (PeopleOrganizationsInline,)

class OrganizationAdmin(admin.ModelAdmin):
    model = Organization
    inlines = (OrganizationAliasesInline,)


admin.site.register(ContactGroup)
admin.site.register(OrganizationDepartment)
admin.site.register(EmailAddress)
admin.site.register(PhoneNumber)
admin.site.register(Place)
admin.site.register(URL)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Person, PersonAdmin)
