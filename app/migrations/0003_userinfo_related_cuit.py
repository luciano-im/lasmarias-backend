# Generated by Django 2.1.2 on 2019-06-07 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20190509_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='related_cuit',
            field=models.CharField(default=0, max_length=11, verbose_name='CUIT / DNI'),
        ),
    ]