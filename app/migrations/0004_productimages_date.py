# Generated by Django 2.1.2 on 2019-06-27 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_userinfo_related_cuit'),
    ]

    operations = [
        migrations.AddField(
            model_name='productimages',
            name='date',
            field=models.DateField(auto_now=True, verbose_name='Fecha de Creación / Actualización'),
        ),
    ]
