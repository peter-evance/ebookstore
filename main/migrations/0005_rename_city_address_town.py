# Generated by Django 4.1.2 on 2022-10-07 04:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_rename_billing_address1_order_billing_address_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='city',
            new_name='town',
        ),
    ]