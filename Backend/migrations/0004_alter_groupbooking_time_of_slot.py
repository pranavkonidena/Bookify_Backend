# Generated by Django 4.2.4 on 2023-10-03 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0003_notallowedtimes_remove_amenity_allowed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupbooking',
            name='time_of_slot',
            field=models.TimeField(),
        ),
    ]
