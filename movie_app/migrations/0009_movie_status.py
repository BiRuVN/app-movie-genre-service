# Generated by Django 3.2 on 2021-06-12 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_app', '0008_auto_20210505_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='status',
            field=models.IntegerField(choices=[(1, 'NOT_SHOW'), (2, 'IS_SHOWING'), (3, 'WILL_SHOW')], default=3),
        ),
    ]
