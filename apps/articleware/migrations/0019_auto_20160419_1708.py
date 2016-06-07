# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-19 21:08
from __future__ import unicode_literals

from django.db import migrations

def populate_flavor(apps, schema_editor):
    # consolidate, article/blog/page type into the flavor field.
    # We can't import the Article model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Article = apps.get_model("articleware", "Article")
    for article in Article.objects.all():
        if article.blog:
            article.flavor = "Blog"
        elif article.page:
            article.flavor = "Page"
        article.save()

class Migration(migrations.Migration):

    dependencies = [
        ('articleware', '0018_auto_20160419_1706'),
    ]

    operations = [
        migrations.RunPython(populate_flavor),
    ]