# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0006_auto_20150521_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='is_user_menu',
            field=models.BooleanField(default=False, help_text='If this menu is the User Menu, check this box.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='menuentry',
            name='display_options',
            field=models.CharField(default='A', max_length=1, choices=[('A', 'Always display'), ('I', 'Display only to logged-in users'), ('O', 'Display only to anonymous users'), ('S', 'Display only to staff and administrators')]),
            preserve_default=True,
        ),
    ]
