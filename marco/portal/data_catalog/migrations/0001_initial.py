# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0008_populate_latest_revision_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataCatalog',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
