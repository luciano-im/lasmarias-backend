# Generated by Django 2.1.2 on 2019-03-14 00:21

from django.db import migrations, models
import django.db.models.deletion
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_productimages'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productimages',
            options={'verbose_name': 'Imágen', 'verbose_name_plural': 'Imágenes'},
        ),
        migrations.AlterField(
            model_name='productimages',
            name='image',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, max_length=200, null=True, quality=0, size=[200, 200], upload_to='images/', verbose_name='Imágen'),
        ),
        migrations.AlterField(
            model_name='productimages',
            name='product_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Products', verbose_name='Producto'),
        ),
    ]