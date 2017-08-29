from django.contrib import admin
from .models import (
    ContactGroup,
    OrganizationDepartment,
    EmailAddress,
    PhoneNumber,
    URL,
    Organization,
    OrganizationAlias,
    Person
)

admin.site.register(ContactGroup)
admin.site.register(OrganizationDepartment)
admin.site.register(EmailAddress)
admin.site.register(PhoneNumber)
admin.site.register(URL)
admin.site.register(Organization)
admin.site.register(OrganizationAlias)
admin.site.register(Person)
