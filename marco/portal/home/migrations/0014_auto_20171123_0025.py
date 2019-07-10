# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.core.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0023_alter_page_revision_on_delete_behaviour'),
        # RDH I'm restarting the base migrations due to incompatibility with django/wagtail upgrade
        ('base', '__first__'),
        # ('base', '0004_auto_20171120_2310'),
        ('home', '0013_auto_20171123_0013'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomePageCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('body', wagtail.core.fields.RichTextField(null=True, blank=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('card_image', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.PortalImage', null=True)),
                ('link_page', models.ForeignKey(related_name='+', blank=True, to='wagtailcore.Page', null=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='homepagecards',
            name='card_center',
        ),
        migrations.RemoveField(
            model_name='homepagecards',
            name='card_image',
        ),
        migrations.RemoveField(
            model_name='homepagecards',
            name='card_left',
        ),
        migrations.RemoveField(
            model_name='homepagecards',
            name='card_right',
        ),
        migrations.RemoveField(
            model_name='homepagecards',
            name='link_page',
        ),
        migrations.DeleteModel(
            name='HomePageCards',
        ),
        migrations.AddField(
            model_name='homepage',
            name='card_center',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='home.HomePageCard', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='homepage',
            name='card_left',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='home.HomePageCard', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='homepage',
            name='card_right',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='home.HomePageCard', null=True),
            preserve_default=True,
        ),
    ]
