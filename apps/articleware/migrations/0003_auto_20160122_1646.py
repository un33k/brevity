# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-22 21:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articleware', '0002_auto_20160120_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.CharField(choices=[('Public', 'Public'), ('Unlisted', 'Unlisted'), ('Private', 'Private')], default='Private', help_text='View Status. Public=ByAll, Unlisted=ByUrlHolders, Private=ByNoone.', max_length=20, verbose_name='Status'),
        ),
    ]