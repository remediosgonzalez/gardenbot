# Generated by Django 3.0.7 on 2020-06-27 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20200627_1838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='balance',
            field=models.IntegerField(null=True),
        ),
    ]