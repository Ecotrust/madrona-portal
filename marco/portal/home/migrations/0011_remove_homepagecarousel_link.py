# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_auto_20171121_2246'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homepagecarousel',
            name='link',
        ),
    ]
