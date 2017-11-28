# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20150122_2130'),
        ('home', '0003_homepagecarousel'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='description',
            field=wagtail.wagtailcore.fields.RichTextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='homepage',
            name='feature_image',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.PortalImage', null=True),
            preserve_default=True,
        ),
    ]
