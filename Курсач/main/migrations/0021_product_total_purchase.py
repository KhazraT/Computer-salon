# Generated by Django 5.0.4 on 2024-05-24 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_order_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='total_purchase',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
