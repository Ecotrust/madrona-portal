# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # RDH I'm restarting the base migrations due to incompatibility with django/wagtail upgrade
        ('base', '__first__'),
        # ('base', '0003_auto_20150122_2130'),
        ('ocean_stories', '0006_auto_20150121_2319'),
    ]

    operations = [
        migrations.AddField(
            model_name='oceanstorysection',
            name='media_caption',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='oceanstorysection',
            name='media_embed_url',
            field=models.URLField(verbose_name='Embed URL', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='oceanstorysection',
            name='media_image',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.PortalImage', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='oceanstorysection',
            name='media_position',
            field=models.CharField(default='left', max_length=8, choices=[('left', 'left'), ('right', 'right'), ('full', 'full')]),
            preserve_default=True,
        ),
    ]
