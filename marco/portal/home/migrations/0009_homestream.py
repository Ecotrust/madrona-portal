# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
if settings.WAGTAIL_VERSION > 1:
    import wagtail.core.fields as wagtail_core_fields
    import wagtail.core.blocks as wagtail_core_blocks
    import wagtail.images.blocks as wagtail_images_blocks
else:
    import wagtail.wagtailcore.fields as wagtail_core_fields
    import wagtail.wagtailcore.blocks as wagtail_core_blocks
    import wagtail.wagtailimages.blocks as wagtail_images_blocks
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0023_alter_page_revision_on_delete_behaviour'),
        ('home', '0008_auto_20171121_0042'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomeStream',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page', on_delete=django.db.models.deletion.CASCADE)),
                ('home_body', wagtail_core_fields.StreamField([('heading', wagtail_core_blocks.CharBlock(classname='full title')), ('paragraph', wagtail_core_blocks.RichTextBlock()), ('image', wagtail_images_blocks.ImageChooserBlock())])),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
