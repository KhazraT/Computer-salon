# Generated by Django 5.0.4 on 2024-05-24 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_merge_20240524_1937'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='date_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
