# Generated by Django 5.0.4 on 2024-05-24 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_remove_user_credit_limit_remove_user_credit_remain_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='total_purchase',
        ),
        migrations.AddField(
            model_name='user',
            name='total_purchase',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
