# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data_gaps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='datagaps',
            name='description',
            field=wagtail.core.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='datagap',
            name='description',
            field=wagtail.core.fields.RichTextField(),
            preserve_default=True,
        ),
    ]
