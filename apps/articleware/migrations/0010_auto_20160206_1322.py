# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-06 18:22
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articleware', '0009_auto_20160205_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='like',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='snippet',
            name='content',
            field=models.TextField(blank=True, help_text='Content for this snippet.', null=True, validators=[django.core.validators.MaxLengthValidator(10000)], verbose_name='content'),
        ),
    ]
