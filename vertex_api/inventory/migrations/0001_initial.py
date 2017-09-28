# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-28 19:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('places', '0002_country_locality_route'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('contacts', '0010_hardwaresupplier'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='places.Place', verbose_name='Location')),
            ],
            options={
                'verbose_name': 'Inventory',
                'verbose_name_plural': 'Inventories',
            },
        ),
        migrations.CreateModel(
            name='InventoryCheckPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date & time')),
                ('inventory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Inventory', verbose_name='Inventory')),
            ],
        ),
        migrations.CreateModel(
            name='InventoryCPQty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(verbose_name='Quantity')),
                ('check_point', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.InventoryCheckPoint', verbose_name='Check point')),
            ],
        ),
        migrations.CreateModel(
            name='InventoryTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(verbose_name='Quantity')),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='Date')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('inventory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='inventory.Inventory', verbose_name='Inventory')),
            ],
            options={
                'verbose_name': 'Inventory transaction',
                'verbose_name_plural': 'Inventory transactions',
                'ordering': ['-date', '-id'],
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('modified_at', models.DateTimeField(auto_now=True, null=True, verbose_name='modified at')),
                ('asset_tag', models.SlugField(max_length=8, verbose_name='Asset tag')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('serial_number', models.CharField(blank=True, max_length=48, null=True, verbose_name='Serial number')),
                ('active', models.BooleanField(default=True)),
                ('assigned_to', models.ManyToManyField(blank=True, related_name='items', to='contacts.Organization', verbose_name='Asset number')),
            ],
            options={
                'verbose_name': 'Asset',
                'verbose_name_plural': 'Assets',
                'ordering': ['asset_tag'],
            },
        ),
        migrations.CreateModel(
            name='ItemGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
                ('items', models.ManyToManyField(blank=True, to='inventory.Item', verbose_name='Items')),
            ],
            options={
                'verbose_name': 'Item group',
                'verbose_name_plural': 'Item groups',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ItemState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True, verbose_name='Date')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Item', verbose_name='Item')),
            ],
            options={
                'verbose_name': 'Item state',
                'verbose_name_plural': 'Item state',
            },
        ),
        migrations.CreateModel(
            name='ItemTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('modified_at', models.DateTimeField(auto_now=True, null=True, verbose_name='modified at')),
                ('description', models.CharField(max_length=64, verbose_name='Description')),
                ('model', models.CharField(max_length=50)),
                ('slug', models.SlugField(unique=True)),
                ('part_number', models.CharField(blank=True, help_text='Discrete part number (optional)', max_length=50)),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('manufacturer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='item_templates', to='contacts.Manufacturer')),
                ('suppliers', models.ManyToManyField(blank=True, to='contacts.HardwareSupplier', verbose_name='Suppliers')),
                ('supplies', models.ManyToManyField(blank=True, related_name='_itemtemplate_supplies_+', to='inventory.ItemTemplate', verbose_name='Supplies')),
            ],
            options={
                'verbose_name': 'Item template',
                'verbose_name_plural': 'Item templates',
                'ordering': ['manufacturer', 'model'],
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timedate', models.DateTimeField(auto_now_add=True, verbose_name='Date & time')),
                ('action', models.CharField(max_length=32, verbose_name='Action')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='User defined ID')),
                ('issue_date', models.DateField(auto_now_add=True, verbose_name='Issue date')),
                ('required_date', models.DateField(blank=True, null=True, verbose_name='Date required')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
            ],
            options={
                'verbose_name': 'Purchase order',
                'verbose_name_plural': 'Purchase orders',
            },
        ),
        migrations.CreateModel(
            name='PurchaseOrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agreed_price', models.PositiveIntegerField(blank=True, null=True, verbose_name='Agreed price')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('qty', models.PositiveIntegerField(verbose_name='Quantity')),
                ('received_qty', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='received')),
                ('item_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.ItemTemplate', verbose_name='Item template')),
                ('purchase_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='inventory.PurchaseOrder', verbose_name='Purchase order')),
            ],
            options={
                'verbose_name': 'Purchase order item',
                'verbose_name_plural': 'Purchase order items',
            },
        ),
        migrations.CreateModel(
            name='PurchaseOrderItemStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Purchase order item status',
                'verbose_name_plural': 'Purchase order item status',
            },
        ),
        migrations.CreateModel(
            name='PurchaseOrderStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Purchase order status',
                'verbose_name_plural': 'Purchase order status',
            },
        ),
        migrations.CreateModel(
            name='PurchaseRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='User defined ID (optional)')),
                ('issue_date', models.DateField(auto_now_add=True, verbose_name='Issue date')),
                ('required_date', models.DateField(blank=True, null=True, verbose_name='Date required')),
                ('budget', models.PositiveIntegerField(blank=True, null=True, verbose_name='Budget')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('originator', models.CharField(blank=True, max_length=64, null=True, verbose_name='Originator')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
            ],
            options={
                'verbose_name': 'Purchase request',
                'verbose_name_plural': 'Purchase requests',
            },
        ),
        migrations.CreateModel(
            name='PurchaseRequestItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.PositiveIntegerField(verbose_name='Quantity')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('item_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.ItemTemplate', verbose_name='Item template')),
                ('purchase_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='inventory.PurchaseRequest', verbose_name='Purchase request')),
            ],
            options={
                'verbose_name': 'Purchase request item',
                'verbose_name_plural': 'Purchase request items',
            },
        ),
        migrations.CreateModel(
            name='PurchaseRequestStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Purchase request status',
                'verbose_name_plural': 'Purchase request status',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
                ('exclusive', models.BooleanField(default=False, verbose_name='Exclusive')),
            ],
            options={
                'verbose_name': 'Asset state',
                'verbose_name_plural': 'Asset states',
            },
        ),
        migrations.AddField(
            model_name='purchaserequest',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.PurchaseRequestStatus', verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='purchaseorderitem',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.PurchaseOrderItemStatus', verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='purchase_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.PurchaseRequest', verbose_name='Purchase request'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.PurchaseOrderStatus', verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_orders', to='contacts.HardwareSupplier', verbose_name='Supplier'),
        ),
        migrations.AddField(
            model_name='itemstate',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.State', verbose_name='State'),
        ),
        migrations.AddField(
            model_name='item',
            name='item_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='inventory.ItemTemplate', verbose_name='Item template'),
        ),
        migrations.AddField(
            model_name='item',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='places.Place', verbose_name='General location'),
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='supply',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.ItemTemplate', verbose_name='Supply'),
        ),
        migrations.AddField(
            model_name='inventorycpqty',
            name='supply',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.ItemTemplate', verbose_name='Supply'),
        ),
        migrations.AddField(
            model_name='inventorycheckpoint',
            name='supplies',
            field=models.ManyToManyField(blank=True, through='inventory.InventoryCPQty', to='inventory.ItemTemplate', verbose_name='Supplies'),
        ),
        migrations.AlterUniqueTogether(
            name='itemtemplate',
            unique_together=set([('manufacturer', 'model')]),
        ),
        migrations.AlterUniqueTogether(
            name='item',
            unique_together=set([('item_template', 'serial_number')]),
        ),
    ]
