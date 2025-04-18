# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
if settings.WAGTAIL_VERSION > 1:
    import wagtail.fields as wagtail_core_fields
else:
    import wagtail.fields as wagtail_core_fields
import modelcluster.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0008_populate_latest_revision_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='OceanStories',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='OceanStory',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='OceanStorySection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('title', models.CharField(max_length=255)),
                ('body', wagtail_core_fields.RichTextField()),
                ('map_state', models.TextField()),
                ('page', modelcluster.fields.ParentalKey(related_name='sections', to='ocean_stories.OceanStory')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
