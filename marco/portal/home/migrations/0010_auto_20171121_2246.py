# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
if settings.WAGTAIL_VERSION > 1:
    import wagtail.core.fields as wagtail_core_fields
else:
    import wagtail.core.fields as wagtail_core_fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0023_alter_page_revision_on_delete_behaviour'),
        ('wagtailforms', '0003_capitalizeverbose'),
        ('wagtailredirects', '0005_capitalizeverbose'),
        ('home', '0009_homestream'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homestream',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='HomeStream',
        ),
        migrations.AddField(
            model_name='homepage',
            name='intro',
            field=wagtail_core_fields.RichTextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='homepagecarousel',
            name='link_external',
            field=models.URLField(verbose_name='External link', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='homepagecarousel',
            name='link_page',
            field=models.ForeignKey(related_name='+', blank=True, to='wagtailcore.Page', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
    ]
