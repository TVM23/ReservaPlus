# Generated by Django 5.1.1 on 2024-10-16 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HotelApp', '0007_servicios_precio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detallehabitacion',
            name='habitaciones_disponibles',
        ),
        migrations.AddField(
            model_name='detallehabitacion',
            name='disponibilidad',
            field=models.CharField(default='disponible', max_length=20),
        ),
    ]