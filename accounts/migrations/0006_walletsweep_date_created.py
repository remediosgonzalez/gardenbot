# Generated by Django 3.0.8 on 2020-08-07 06:26

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20200628_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='walletsweep',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]