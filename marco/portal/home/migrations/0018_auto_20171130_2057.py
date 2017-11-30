# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0017_auto_20171130_2030'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homepage',
            name='card_center',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='card_left',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='card_right',
        ),
    ]
