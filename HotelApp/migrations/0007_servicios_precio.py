# Generated by Django 5.1.1 on 2024-10-15 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HotelApp', '0006_detallehabitacion_numero_de_habitacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicios',
            name='precio',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
