# Generated by Django 4.1.2 on 2022-10-06 13:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20210825_0706'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='billing_address1',
            new_name='billing_address',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='billing_city',
            new_name='billing_town',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='shipping_address1',
            new_name='shipping_address',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='shipping_city',
            new_name='shipping_town',
        ),
        migrations.RemoveField(
            model_name='address',
            name='address1',
        ),
        migrations.RemoveField(
            model_name='address',
            name='address2',
        ),
        migrations.RemoveField(
            model_name='address',
            name='country',
        ),
        migrations.RemoveField(
            model_name='address',
            name='zip_code',
        ),
        migrations.RemoveField(
            model_name='order',
            name='billing_address2',
        ),
        migrations.RemoveField(
            model_name='order',
            name='billing_zip_code',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_address2',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_zip_code',
        ),
        migrations.AddField(
            model_name='address',
            name='address',
            field=models.CharField(default=django.utils.timezone.now, max_length=60, verbose_name='Address line'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='county',
            field=models.CharField(choices=[('ksm', 'Kisumu'), ('nrb', 'Nairobi'), ('mbm', 'Mombasa'), ('nkr', 'Nakuru'), ('mig', 'Migori')], default=django.utils.timezone.now, max_length=3),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(max_length=35),
        ),
        migrations.AlterField(
            model_name='address',
            name='name',
            field=models.CharField(max_length=35),
        ),
    ]