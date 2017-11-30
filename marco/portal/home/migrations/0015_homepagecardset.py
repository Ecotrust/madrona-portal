# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_auto_20171123_0025'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomePageCardSet',
            fields=[
                ('homepagecard_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='home.HomePageCard')),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('cards', modelcluster.fields.ParentalKey(related_name='cards', to='home.HomePage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
            bases=('home.homepagecard', models.Model),
        ),
    ]
