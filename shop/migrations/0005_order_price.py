# Generated by Django 3.0.7 on 2020-06-28 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_auto_20200627_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='price',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
