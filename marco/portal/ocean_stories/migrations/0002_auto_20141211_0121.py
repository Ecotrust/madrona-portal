# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocean_stories', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oceanstorysection',
            name='title',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
