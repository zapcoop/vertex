from django.conf import settings
from django.db import models
from django.urls import reverse

from circuits.utils import get_default_renewal_date
from vertex.models import AbstractDatedModel
from .constants import *


class CircuitType(models.Model):
    """
    Circuits can be organized by their functional role. For example, a user might wish to define
    CircuitTypes named
    "Long Haul," "Metro," or "Out-of-Band".
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Circuit(AbstractDatedModel):
    """
    A communications circuit connects two points. Each Circuit belongs to a Provider; Providers
    may have multiple
    circuits. Each circuit is also assigned a CircuitType and a Site. A Circuit may be terminated
    to a specific device
    interface, but this is not required. Circuit port speed and commit rate are measured in Kbps.
    """
    circuit_id = models.CharField(max_length=50, verbose_name='Circuit ID')
    provider = models.ForeignKey('contacts.TelecomProvider', related_name='circuits',
                                 on_delete=models.PROTECT)
    type = models.ForeignKey('CircuitType', related_name='circuits', on_delete=models.PROTECT)
    install_date = models.DateField(blank=True, null=True, verbose_name='Date installed',
                                    auto_now_add=True)
    renewal_date = models.DateField(blank=True, null=True, verbose_name='Renewal date',
                                    default=get_default_renewal_date)

    contract_renewal = models.CharField(
        max_length=2,
        default=(settings.DEFAULT_CIRCUITS_RENEWAL or RENEWAL_MONTHLY),
        choices=RENEWAL_TYPE_CHOICES
    )

    upload_rate = models.PositiveIntegerField(blank=True, null=True,
                                              verbose_name='Upload rate (Kbps)')
    download_rate = models.PositiveIntegerField(blank=True, null=True,
                                                verbose_name='Download rate (Kbps)')

    description = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['provider', 'cid']
        unique_together = ['provider', 'cid']

    def __str__(self):
        return '{} {}'.format(self.provider, self.circuit_id)

    def _get_termination(self, side):
        for ct in self.terminations.all():
            if ct.term_side == side:
                return ct
        return None

    @property
    def termination_a(self):
        return self._get_termination('A')

    @property
    def termination_z(self):
        return self._get_termination('Z')


class CircuitTermination(models.Model):
    circuit = models.ForeignKey('Circuit', related_name='terminations', on_delete=models.CASCADE)
    term_side = models.CharField(max_length=1, choices=TERM_SIDE_CHOICES,
                                 verbose_name='Termination')
    space = models.ForeignKey('ipam.Space', related_name='circuit_terminations',
                              on_delete=models.PROTECT)
    interface = models.OneToOneField(
        'infrastructure.Interface', related_name='circuit_termination', blank=True, null=True,
        on_delete=models.PROTECT
    )
    port_speed = models.PositiveIntegerField(verbose_name='Port speed (Kbps)')

    class Meta:
        ordering = ['circuit', 'term_side']
        unique_together = ['circuit', 'term_side']

    def __str__(self):
        return '{} (Side {})'.format(self.circuit, self.get_term_side_display())

    def get_peer_termination(self):
        peer_side = 'Z' if self.term_side == 'A' else 'A'
        try:
            return CircuitTermination.objects.select_related('site').get(circuit=self.circuit,
                                                                         term_side=peer_side)
        except CircuitTermination.DoesNotExist:
            return None
