# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
if settings.WAGTAIL_VERSION > 1:
    import wagtail.core.fields as wagtail_core_fields
else:
    import wagtail.wagtailcore.fields as wagtail_core_fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # RDH I'm restarting the base migrations due to incompatibility with django/wagtail upgrade
        ('base', '__first__'),
        # ('base', '0003_auto_20150122_2130'),
        ('home', '0003_homepagecarousel'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='description',
            field=wagtail_core_fields.RichTextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='homepage',
            name='feature_image',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.PortalImage', null=True),
            preserve_default=True,
        ),
    ]
