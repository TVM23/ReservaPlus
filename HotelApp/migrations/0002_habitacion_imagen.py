# Generated by Django 5.1.1 on 2024-10-03 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HotelApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='habitacion',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='habitaciones/'),
        ),
    ]
