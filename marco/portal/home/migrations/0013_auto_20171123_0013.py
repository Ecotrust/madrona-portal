# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_homepagecards'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='homepagecards',
            options={'ordering': ['sort_order']},
        ),
        migrations.AddField(
            model_name='homepagecards',
            name='sort_order',
            field=models.IntegerField(null=True, editable=False, blank=True),
            preserve_default=True,
        ),
    ]
