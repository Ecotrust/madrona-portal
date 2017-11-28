# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_auto_20171118_0027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homepage',
            name='feature_image',
        ),
    ]
