from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from vertex.models import AbstractDatedModel


class State(models.Model):
    name = models.CharField(max_length=32, verbose_name=_('Name'))
    exclusive = models.BooleanField(default=False, verbose_name=_('Exclusive'))

    class Meta:
        verbose_name = _('Asset state')
        verbose_name_plural = _('Asset states')
        app_label = 'inventory'

    def __str__(self):
        return '{name} ({status})'.format(
            name=self.name,
            status=_('Exclusive') if self.exclusive else _('Inclusive')
        )


class AssetStateManager(models.Manager):
    def states_for_asset(self, asset):
        return self.filter(asset=asset)


class AssetState(models.Model):
    asset = models.ForeignKey('inventory.Asset', verbose_name=_('Asset'))
    state = models.ForeignKey(State, verbose_name=_('State'))
    date = models.DateField(auto_now_add=True, verbose_name=_('Date'))

    objects = AssetStateManager()

    class Meta:
        verbose_name = _('Asset state association')
        verbose_name_plural = _('Asset state associations')
        app_label = 'inventory'

    def __str__(self):
        return _('%(asset)s, %(state)s since %(date)s') % {'asset': self.asset,
                                                           'state': self.state.name,
                                                           'date': self.date}


class Asset(AbstractDatedModel):
    base_item = models.ForeignKey('inventory.BaseItem', related_name='assets',
                                  verbose_name=_('Base item'))
    asset_tag = models.SlugField(max_length=8, verbose_name=_('Asset tag'), editable=False)
    notes = models.TextField(blank=True, null=True, verbose_name=_('Notes'))

    serial_number = models.CharField(blank=True, max_length=48, null=True,
                                     verbose_name=_('Serial number'))

    assigned_to = models.ManyToManyField('contacts.Organization', verbose_name=_('Assigned to'),
                                         blank=True, related_name='items')

    location = models.ForeignKey('places.Place', blank=True, null=True,
                                 verbose_name=_('General location'))

    active = models.BooleanField(default=True)

    def clean(self):
        pass
        # TODO - Figure out / validate if location is owned by Assigned Org.

    def generate_asset_tag(self):
        if self.pk is None and not self.asset_tag:
            asset_tag = "A-" + get_random_string(
                length=6,
                allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ0123456789'
            )
            if self.__class__.objects.filter(asset_tag=asset_tag).exists():
                self.generate_asset_tag()
            else:
                self.asset_tag = asset_tag

    def save(self, *args, **kwargs):
        self.generate_asset_tag()
        super().save(*args, **kwargs)

    def __str__(self):
        states = ', '.join(
            [assetstate.state.name for assetstate in AssetState.objects.states_for_asset(self)])
        return "#%s, '%s' %s" % (
            self.asset_tag, self.base_item.description, states and '(%s)' % states)

    @property
    def is_orphan(self):
        return not self.assigned_to.exists()

    @property
    def states(self):
        return [State.objects.get(pk=pk) for pk in
                self.assetstate_set.all().values_list('state', flat=True)]

    class Meta:
        ordering = ['asset_tag']
        unique_together = (('base_item', 'serial_number'))
        verbose_name = _('Asset')
        verbose_name_plural = _('Assets')
        app_label = 'inventory'


class AssetGroup(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=32)
    assets = models.ManyToManyField(Asset, blank=True, verbose_name=_('Assets'))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _('Asset group')
        verbose_name_plural = _('Asset groups')
        app_label = 'inventory'

#
# register(AssetState, _('Asset states'), ['state__name'])
# register(Asset, _('Assets'),
#          ['property_number', 'notes', 'serial_number', 'person__first_name', 'person__last_name',
#           'person__second_last_name', 'person__second_name'])
# register(AssetGroup, _('Asset groups'), ['name'])
# register(Person, _('People'),
#          ['last_name', 'second_last_name', 'first_name', 'second_name', 'location__name'])
