# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0015_homepagecardset'),
    ]

    operations = [
        migrations.RenameField(
            model_name='homepagecard',
            old_name='card_image',
            new_name='feature_image',
        ),
    ]
