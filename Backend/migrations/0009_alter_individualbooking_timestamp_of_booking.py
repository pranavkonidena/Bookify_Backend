# Generated by Django 4.2.4 on 2023-11-15 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0008_alter_user_credits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='individualbooking',
            name='timestamp_of_booking',
            field=models.DateTimeField(),
        ),
    ]
