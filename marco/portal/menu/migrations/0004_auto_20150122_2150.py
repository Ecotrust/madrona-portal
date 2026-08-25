# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0003_menuentry_page'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuentry',
            name='title',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
