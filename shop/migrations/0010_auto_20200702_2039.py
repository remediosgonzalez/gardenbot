# Generated by Django 3.0.7 on 2020-07-02 17:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_auto_20200702_1345'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='photo_file_unique_id',
            new_name='photo_file_id',
        ),
    ]
