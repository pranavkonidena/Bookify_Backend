# Generated by Django 4.2.4 on 2023-11-09 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0007_amenity_credits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='credits',
            field=models.IntegerField(default=50),
        ),
    ]
