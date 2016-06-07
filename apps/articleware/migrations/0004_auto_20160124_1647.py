# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-24 21:47
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articleware', '0003_auto_20160122_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='headline',
            field=models.TextField(help_text='Headline for this post', validators=[django.core.validators.MinLengthValidator(10), django.core.validators.MaxLengthValidator(120)], verbose_name='Headline'),
        ),
    ]