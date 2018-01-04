from django.contrib import admin

from infrastructure.models import (
    DeviceDefinition,
    InterfaceTemplate,
    SerialPortTemplate,
    PowerPortTemplate,
    PowerOutletTemplate,
    Interface,
    InterfaceConnection,
    Device,
    DeviceRole,
    Platform,
    PowerOutlet,
    PowerPort,
    SerialPort
)


class InterfaceInline(admin.StackedInline):
    model = Interface
    extra = 0


class PowerOutletInline(admin.StackedInline):
    model = PowerOutlet
    extra = 0


class PowerPortInline(admin.StackedInline):
    model = PowerPort
    extra = 0


class SerialPortInline(admin.StackedInline):
    model = SerialPort
    extra = 0


class InterfaceTemplateInline(admin.StackedInline):
    model = InterfaceTemplate
    extra = 0


class SerialPortTemplateInline(admin.StackedInline):
    model = SerialPortTemplate
    extra = 0


class PowerPortTemplateInline(admin.StackedInline):
    model = PowerPortTemplate
    extra = 0


class PowerOutletTemplateInline(admin.StackedInline):
    model = PowerOutletTemplate
    extra = 0


class DeviceDefinitionAdmin(admin.ModelAdmin):
    inlines = (InterfaceTemplateInline, SerialPortTemplateInline, PowerPortTemplateInline,
               PowerOutletTemplateInline)


class DeviceAdmin(admin.ModelAdmin):
    inlines = (InterfaceInline, SerialPortInline, PowerPortInline,
               PowerOutletInline)


admin.site.register(DeviceDefinition, DeviceDefinitionAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(InterfaceConnection)
admin.site.register(DeviceRole)
admin.site.register(Platform)
