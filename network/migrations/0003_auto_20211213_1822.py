# Generated by Django 3.1.5 on 2021-12-14 00:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_follow_like_post'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together={('follower_user', 'follows_user')},
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together={('user', 'post')},
        ),
    ]
