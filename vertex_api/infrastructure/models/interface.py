
@python_2_unicode_compatible
class Interface(models.Model):
    """
    A physical data interface within a Device. An Interface can connect to exactly one other Interface via the creation
    of an InterfaceConnection.
    """
    device = models.ForeignKey('Device', related_name='interfaces', on_delete=models.CASCADE)
    lag = models.ForeignKey(
        'self',
        models.SET_NULL,
        related_name='member_interfaces',
        null=True,
        blank=True,
        verbose_name='Parent LAG'
    )
    name = models.CharField(max_length=64)
    form_factor = models.PositiveSmallIntegerField(choices=IFACE_FF_CHOICES,
                                                   default=IFACE_FF_10GE_SFP_PLUS)
    enabled = models.BooleanField(default=True)
    mac_address = MACAddressField(null=True, blank=True, verbose_name='MAC Address')
    mtu = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='MTU')
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name='OOB Management',
        help_text="This interface is used only for out-of-band management"
    )
    description = models.CharField(max_length=100, blank=True)

    objects = InterfaceQuerySet.as_manager()

    class Meta:
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    def clean(self):

        # Virtual interfaces cannot be connected
        if self.form_factor in NONCONNECTABLE_IFACE_TYPES and self.is_connected:
            raise ValidationError({
                'form_factor': "Virtual and wireless interfaces cannot be connected to another interface or circuit. "
                               "Disconnect the interface or choose a suitable form factor."
            })

        # An interface's LAG must belong to the same device
        if self.lag and self.lag.device != self.device:
            raise ValidationError({
                'lag': "The selected LAG interface ({}) belongs to a different device ({}).".format(
                    self.lag.name, self.lag.device.name
                )
            })

        # A virtual interface cannot have a parent LAG
        if self.form_factor in NONCONNECTABLE_IFACE_TYPES and self.lag is not None:
            raise ValidationError({
                'lag': "{} interfaces cannot have a parent LAG interface.".format(
                    self.get_form_factor_display())
            })

        # Only a LAG can have LAG members
        if self.form_factor != IFACE_FF_LAG and self.member_interfaces.exists():
            raise ValidationError({
                'form_factor': "Cannot change interface form factor; it has LAG members ({}).".format(
                    ", ".join([iface.name for iface in self.member_interfaces.all()])
                )
            })

    @property
    def is_virtual(self):
        return self.form_factor in VIRTUAL_IFACE_TYPES

    @property
    def is_wireless(self):
        return self.form_factor in WIRELESS_IFACE_TYPES

    @property
    def is_lag(self):
        return self.form_factor == IFACE_FF_LAG

    @property
    def is_connected(self):
        try:
            return bool(self.circuit_termination)
        except ObjectDoesNotExist:
            pass
        return bool(self.connection)

    @property
    def connection(self):
        try:
            return self.connected_as_a
        except ObjectDoesNotExist:
            pass
        try:
            return self.connected_as_b
        except ObjectDoesNotExist:
            pass
        return None

    @property
    def connected_interface(self):
        try:
            if self.connected_as_a:
                return self.connected_as_a.interface_b
        except ObjectDoesNotExist:
            pass
        try:
            if self.connected_as_b:
                return self.connected_as_b.interface_a
        except ObjectDoesNotExist:
            pass
        return None


class InterfaceConnection(models.Model):
    """
    An InterfaceConnection represents a symmetrical, one-to-one connection between two Interfaces. There is no
    significant difference between the interface_a and interface_b fields.
    """
    interface_a = models.OneToOneField('Interface', related_name='connected_as_a',
                                       on_delete=models.CASCADE)
    interface_b = models.OneToOneField('Interface', related_name='connected_as_b',
                                       on_delete=models.CASCADE)
    connection_status = models.BooleanField(choices=CONNECTION_STATUS_CHOICES,
                                            default=CONNECTION_STATUS_CONNECTED,
                                            verbose_name='Status')

    csv_headers = ['device_a', 'interface_a', 'device_b', 'interface_b', 'connection_status']

    def clean(self):
        try:
            if self.interface_a == self.interface_b:
                raise ValidationError({
                    'interface_b': "Cannot connect an interface to itself."
                })
        except ObjectDoesNotExist:
            pass

    # Used for connections export
    def to_csv(self):
        return csv_format([
            self.interface_a.device.identifier,
            self.interface_a.name,
            self.interface_b.device.identifier,
            self.interface_b.name,
            self.get_connection_status_display(),
        ])

