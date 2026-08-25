# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grid_pages', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gridpagedetail',
            old_name='target_year',
            new_name='metric',
        ),
    ]
