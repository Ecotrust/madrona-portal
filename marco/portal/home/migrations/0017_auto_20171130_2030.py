# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_auto_20171130_1854'),
    ]

    operations = [
        migrations.RenameField(
            model_name='homepagecard',
            old_name='body',
            new_name='description',
        ),
    ]
