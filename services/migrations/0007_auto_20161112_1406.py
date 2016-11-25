# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-12 14:06
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_auto_20161112_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
