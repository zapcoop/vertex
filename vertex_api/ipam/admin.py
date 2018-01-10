from django.contrib import admin
from ipam.models import Subnet, IPAddress, IPRange, Space, VLAN, Fabric, MACAddress, VRF, Role

from django.utils.translation import ugettext_lazy as _


class SubnetInline(admin.TabularInline):
    model = Subnet
    extra = 1
    fields = ('name', 'cidr', 'description')


class IPAddressInline(admin.TabularInline):
    model = IPAddress
    extra = 1


class IPRangeInline(admin.TabularInline):
    model = IPRange
    extra = 1


class SubnetAdmin(admin.ModelAdmin):
    list_display = ('name', 'supernet', 'cidr', 'description')
    ordering = ('cidr',)
    inlines = (SubnetInline, IPAddressInline, IPRangeInline)

    list_filter = ('supernet', 'version')

    # def display_with_ancestors(self):
    #     return self.display_with_ancestors()
    # display_with_ancestors.short_description = _("Subnet")


admin.site.register(Subnet, SubnetAdmin)
admin.site.register(IPAddress)
admin.site.register(IPRange)
admin.site.register(Space)
admin.site.register(Fabric)
admin.site.register(VLAN)
admin.site.register(VRF)
admin.site.register(MACAddress)
admin.site.register(Role)
