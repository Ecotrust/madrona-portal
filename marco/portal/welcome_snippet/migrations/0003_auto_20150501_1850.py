# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('welcome_snippet', '0002_welcomepage_use_on_site'),
    ]

    operations = [
        migrations.RenameField(
            model_name='welcomepage',
            old_name='use_on_site',
            new_name='active',
        ),
    ]
