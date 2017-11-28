# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20150122_2130'),
        ('home', '0005_remove_homepage_feature_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homepage',
            name='description',
        ),
        migrations.RemoveField(
            model_name='homepagecarousel',
            name='media_caption',
        ),
        migrations.RemoveField(
            model_name='homepagecarousel',
            name='media_embed_url',
        ),
        migrations.RemoveField(
            model_name='homepagecarousel',
            name='media_image',
        ),
        migrations.RemoveField(
            model_name='homepagecarousel',
            name='media_position',
        ),
        migrations.RemoveField(
            model_name='homepagecarousel',
            name='slide',
        ),
        migrations.AddField(
            model_name='homepagecarousel',
            name='link',
            field=models.URLField(verbose_name=b'Link', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='homepagecarousel',
            name='slide_image',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='base.PortalImage', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='homepagecarousel',
            name='slides',
            field=modelcluster.fields.ParentalKey(related_name='slides', default=1, to='home.HomePage'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='homepagecarousel',
            name='body',
            field=models.CharField(max_length=2000, blank=True),
            preserve_default=True,
        ),
    ]
