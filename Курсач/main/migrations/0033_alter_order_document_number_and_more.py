# Generated by Django 5.0.4 on 2024-05-25 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_returns_document_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='document_number',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='returns',
            name='document_number',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='returns',
            name='return_document_number',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
