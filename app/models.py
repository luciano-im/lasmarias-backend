from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    customer_id = models.CharField(primary_key=True, max_length=6, verbose_name='Código de Cliente')
    cuit = models.CharField(max_length=11, verbose_name='CUIT')
    first_name = models.CharField(max_length=80, verbose_name='Nombre')
    last_name = models.CharField(max_length=80, verbose_name='Apellido')
    zip_code = models.IntegerField(verbose_name='Código Postal')
    telephone = models.CharField(max_length=15, verbose_name='Teléfono')
    discount = models.FloatField(verbose_name='Descuento', help_text='%')

    def __unicode__(self):
        return self.first_name

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'


class Products(models.Model):
    id = models.CharField(primary_key=True, max_length=20, verbose_name='Código de Producto')
    name = models.CharField(max_length=80, verbose_name='Nombre')
    brand = models.CharField(max_length=80, verbose_name='Marca')
    product_line = models.CharField(max_length=80, verbose_name='Rubro')
    unit = models.CharField(max_length=50, verbose_name='Unidad de Medida')
    price = models.FloatField(verbose_name='Precio')
    # image = models.ImageField(verbose_name='Imágen del Producto')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'


class Invoices(models.Model):
    number = models.IntegerField(unique=True, verbose_name='Número de Factura')
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Cliente')
    date = models.DateField(verbose_name='Fecha de Factura')

    def __unicode__(self):
        return self.number

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'


class InvoiceItems(models.Model):
    invoice_number = models.ForeignKey(Invoices, to_field='number', on_delete=models.CASCADE, verbose_name='Número de Factura')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name='Código de Producto')
    price = models.FloatField(verbose_name='Precio')
    quantity = models.FloatField(verbose_name='Cantidad')

    def __unicode__(self):
        return self.invoice_number

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items de Facturas'


class AccountBalance(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Cliente')
    balance = models.FloatField(verbose_name='Saldo Final')

    def __unicode__(self):
        return self.customer_id

    class Meta:
        verbose_name = 'Saldo de Cuenta Corriente'
        verbose_name_plural = 'Saldos de Cuenta Corriente'


class UserInfo(models.Model):
    USER_TYPE = (
        ('VEN', 'Vendedor'),
        ('CMA', 'Cliente Mayorista'),
        ('CMI', 'Cliente Minorista'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Cliente')
    user_type = models.CharField(max_length=3,choices=USER_TYPE, verbose_name='Tipo de Usuario')

    def __unicode__(self):
        return self.customer_id

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
