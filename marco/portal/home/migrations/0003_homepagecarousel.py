# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
if settings.WAGTAIL_VERSION > 1:
    import wagtail.core.fields as wagtail_core_fields
else:
    import wagtail.wagtailcore.fields as wagtail_core_fields
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        # RDH I'm restarting the base migrations due to incompatibility with django/wagtail upgrade
        ('base', '__first__'),
        # ('base', '0003_auto_20150122_2130'),
        ('home', '0002_create_homepage'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomePageCarousel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('media_embed_url', models.URLField(help_text=b"The URL to a video that you'd like to embed, e.g., https://vimeo.com/121095661.", blank=True)),
                ('media_caption', models.CharField(max_length=255, blank=True)),
                ('media_position', models.CharField(default='left', max_length=8, choices=[('left', 'left'), ('right', 'right'), ('full', 'full')])),
                ('title', models.CharField(max_length=255, blank=True)),
                ('body', wagtail_core_fields.RichTextField(blank=True)),
                ('media_image', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.PortalImage', null=True)),
                ('slide', modelcluster.fields.ParentalKey(related_name='slide', to='home.HomePage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
