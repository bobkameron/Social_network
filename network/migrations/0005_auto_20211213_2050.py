# Generated by Django 3.1.5 on 2021-12-14 02:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0004_auto_20211213_2044'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='timestamp',
            new_name='datetime_created',
        ),
    ]
