# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.core.fields
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0023_alter_page_revision_on_delete_behaviour'),
        # RDH I'm restarting the base migrations due to incompatibility with django/wagtail upgrade
        ('base', '__first__'),
        # ('base', '0004_auto_20171120_2310'),
        ('home', '0011_remove_homepagecarousel_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomePageCards',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('body', wagtail.core.fields.RichTextField(null=True, blank=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('card_center', modelcluster.fields.ParentalKey(related_name='card_center', to='home.HomePage')),
                ('card_image', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.PortalImage', null=True)),
                ('card_left', modelcluster.fields.ParentalKey(related_name='card_left', to='home.HomePage')),
                ('card_right', modelcluster.fields.ParentalKey(related_name='card_right', to='home.HomePage')),
                ('link_page', models.ForeignKey(related_name='+', blank=True, to='wagtailcore.Page', null=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
