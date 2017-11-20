from django.contrib import admin

from infrastructure.models import (
    DeviceDefinition,
    InterfaceTemplate,
    SerialPortTemplate,
    PowerPortTemplate,
    PowerOutletTemplate,
    DeviceBayTemplate
)


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


class DeviceBayTemplateInline(admin.StackedInline):
    model = DeviceBayTemplate
    extra = 0


class DeviceDefinitionAdmin(admin.ModelAdmin):
    inlines = (InterfaceTemplateInline, SerialPortTemplateInline, PowerPortTemplateInline,
               PowerOutletTemplateInline, DeviceBayTemplateInline)


admin.site.register(DeviceDefinition, DeviceDefinitionAdmin)
