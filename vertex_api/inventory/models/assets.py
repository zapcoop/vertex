from django.db import models
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


class ItemStateManager(models.Manager):
    def states_for_item(self, item):
        return self.filter(item=item)


class ItemState(models.Model):
    item = models.ForeignKey('inventory.Item', verbose_name=_('Item'))
    state = models.ForeignKey(State, verbose_name=_('State'))
    date = models.DateField(auto_now_add=True, verbose_name=_('Date'))

    objects = ItemStateManager()

    class Meta:
        verbose_name = _('Item state')
        verbose_name_plural = _('Item state')
        app_label = 'inventory'

    def __str__(self):
        return _('%(asset)s, %(state)s since %(date)s') % {'asset': self.item,
                                                           'state': self.state.name,
                                                           'date': self.date}


class Item(AbstractDatedModel):
    item_template = models.ForeignKey('inventory.ItemTemplate', related_name='items',
                                      verbose_name=_('Item template'))
    asset_tag = models.SlugField(max_length=8, verbose_name=_('Asset tag'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Notes'))

    serial_number = models.CharField(blank=True, max_length=48, null=True,
                                     verbose_name=_('Serial number'))

    assigned_to = models.ManyToManyField('contacts.Organization', verbose_name=_('Asset number'),
                                         blank=True, related_name='items')

    location = models.ForeignKey('places.Place', blank=True, null=True,
                                 verbose_name=_('General location'))

    active = models.BooleanField(default=True)

    def clean(self):
        pass
        # TODO - Figure out / validate if location is owned by Assigned Org.

    def save(self, *args, **kwargs):
        # TODO - Set asset tag
        super().save(*args, **kwargs)

    def __str__(self):
        states = ', '.join(
            [itemstate.state.name for itemstate in ItemState.objects.states_for_item(self)])
        return "#%s, '%s' %s" % (
            self.asset_tag, self.item_template.description, states and '(%s)' % states)

    @property
    def is_orphan(self):
        return not self.assigned_to.exists()

    @property
    def states(self):
        return [State.objects.get(pk=pk) for pk in
                self.itemstate_set.all().values_list('state', flat=True)]

    class Meta:
        ordering = ['asset_tag']
        unique_together = (('item_template', 'serial_number'))
        verbose_name = _('Asset')
        verbose_name_plural = _('Assets')
        app_label = 'inventory'


class ItemGroup(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=32)
    items = models.ManyToManyField(Item, blank=True, verbose_name=_('Items'))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _('Item group')
        verbose_name_plural = _('Item groups')
        app_label = 'inventory'

#
# register(ItemState, _('Asset states'), ['state__name'])
# register(Item, _('Assets'),
#          ['property_number', 'notes', 'serial_number', 'person__first_name', 'person__last_name',
#           'person__second_last_name', 'person__second_name'])
# register(ItemGroup, _('Asset groups'), ['name'])
# register(Person, _('People'),
#          ['last_name', 'second_last_name', 'first_name', 'second_name', 'location__name'])
