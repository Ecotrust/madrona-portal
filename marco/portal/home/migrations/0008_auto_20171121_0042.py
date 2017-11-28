# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_auto_20171120_2023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepagecarousel',
            name='link',
            field=models.URLField(null=True, verbose_name=b'Link', blank=True),
            preserve_default=True,
        ),
    ]
