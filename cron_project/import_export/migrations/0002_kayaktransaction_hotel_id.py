# Generated by Django 4.2.17 on 2025-01-12 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('import_export', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kayaktransaction',
            name='hotel_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Hotel ID'),
        ),
    ]
