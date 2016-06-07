# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-17 04:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articleware', '0012_auto_20160209_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.CharField(choices=[('Public', 'Public'), ('Unlisted', 'Unlisted'), ('Private', 'Private'), ('Archived', 'Archived')], default='Unlisted', help_text='Visibility. Public=ByAll, Unlisted=ByLink, Private=ByNobody, Archived=Private+Historical.', max_length=20, verbose_name='Visibility'),
        ),
    ]