# Generated by Django 5.1.1 on 2024-11-05 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reservas', '0006_pago'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pago',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('completado', 'Completado'), ('reembolsado', 'Reembolsado')], max_length=20),
        ),
    ]