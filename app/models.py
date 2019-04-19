from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from django_resized import ResizedImageField


class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True, verbose_name='Código de Cliente')
    cuit = models.CharField(max_length=11, verbose_name='CUIT / DNI')
    name = models.CharField(max_length=120, verbose_name='Nombre')
    address = models.CharField(max_length=150, verbose_name='Dirección')
    city = models.CharField(max_length=80, verbose_name='Localidad')
    zip_code = models.IntegerField(blank=True, null=True, verbose_name='Código Postal')
    telephone = models.CharField(blank=True, null=True, max_length=15, verbose_name='Teléfono')
    email = models.CharField(blank=True, null=True, max_length=50, verbose_name='Email')
    discount = models.FloatField(blank=True, null=True, verbose_name='Descuento')

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'


class Products(models.Model):
    product_id = models.CharField(primary_key=True, max_length=20, verbose_name='Código de Producto')
    name = models.CharField(max_length=80, verbose_name='Nombre')
    brand = models.CharField(max_length=80, verbose_name='Marca')
    product_line = models.CharField(max_length=80, verbose_name='Rubro')
    unit = models.CharField(max_length=50, verbose_name='Unidad de Medida')
    price = models.FloatField(verbose_name='Precio')
    offer = models.BooleanField(default=False, verbose_name='Oferta', help_text='El Producto esta en oferta?')
    offer_price = models.FloatField(default=0, verbose_name='Precio Oferta')
    package = models.CharField(blank=True, null=True, max_length=30, verbose_name='Envase')

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'


def product_image_path(instance, filename):
    return 'products/{0}/{1}'.format(instance.product_id.product_id, filename)

class ProductImages(models.Model):
    # Set related_name to use backward relationships on ProductSerializer
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name='Producto', related_name='images')
    image = ResizedImageField(upload_to=product_image_path, max_length=200, size=[200, 200], blank=True, null=True, verbose_name='Imágen')

    def __str__(self):
        return str('')

    class Meta:
        verbose_name = 'Imágen'
        verbose_name_plural = 'Imágenes'

class Invoices(models.Model):
    number = models.IntegerField(unique=True, verbose_name='Número de Factura')
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Cliente')
    date = models.DateField(verbose_name='Fecha de Factura')

    def get_total(self):
        return sum(item.get_cost() for item in self.items.all())

    def __str__(self):
        return str(self.number)

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'


class InvoiceItems(models.Model):
    invoice_number = models.ForeignKey(Invoices, to_field='number', on_delete=models.CASCADE, verbose_name='Número de Factura', related_name='items')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name='Código de Producto')
    price = models.FloatField(verbose_name='Precio')
    quantity = models.FloatField(verbose_name='Cantidad')

    def get_cost(self):
        return self.price * self.quantity

    def __str__(self):
        return str(self.invoice_number)

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items de Facturas'


class AccountBalance(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Cliente')
    date = models.DateField(verbose_name='Fecha del Comprobante')
    voucher = models.CharField(max_length=30, verbose_name='Comprobante')
    balance = models.FloatField(verbose_name='Saldo')

    def __str__(self):
        return str(self.customer_id)

    class Meta:
        verbose_name = 'Saldo de Cuenta Corriente'
        verbose_name_plural = 'Saldos de Cuenta Corriente'
        unique_together = (('customer_id', 'date', 'voucher'),)


class PaymentMethods(models.Model):
    payment = models.CharField(primary_key=True, max_length=50, verbose_name='Método de Pago')
    sort = models.IntegerField(verbose_name='Orden')

    def __str__(self):
        return str(self.payment)

    class Meta:
        verbose_name = 'Métodos de Pago'
        verbose_name_plural = 'Métodos de Pago'


class OrderStatus(models.Model):
    status = models.CharField(primary_key=True, max_length=30, verbose_name='Estado')
    sort = models.IntegerField(verbose_name='Orden')

    def __str__(self):
        return str(self.status)

    class Meta:
        verbose_name = 'Estado de Pedidos'
        verbose_name_plural = 'Estado de Pedidos'


class Order(models.Model):
    SHIPPING_TYPE = (
        ('ENV', 'Envío'),
        ('REL', 'Retiro en Local'),
    )

    order_id = models.AutoField(primary_key=True, verbose_name='Pedido')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Cliente')
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, verbose_name='Estado')
    payment = models.ForeignKey(PaymentMethods, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Forma de Pago')
    date = models.DateField(verbose_name='Fecha del Pedido')
    discount = models.FloatField(verbose_name='Descuento', help_text='%')
    shipping = models.CharField(max_length=3, choices=SHIPPING_TYPE, verbose_name='Entrega')
    created_at = models.DateTimeField(verbose_name='Fecha/Hora de Creación')

    def get_total(self):
        return sum(item.get_cost() for item in self.items.all())

    def email(self):
        return self.user_id.email

    email.short_description = 'Usuario'

    def __str__(self):
        return str(self.order_id)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        unique_together = (('customer_id', 'created_at'),)


class OrderItems(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Código de Pedido', related_name='items')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name='Código de Producto')
    price = models.FloatField(verbose_name='Precio')
    quantity = models.IntegerField(verbose_name='Cantidad')

    def get_cost(self):
        return round(self.price * self.quantity, 2)

    def __str__(self):
        return str(self.order_id)

    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedidos'


class UserInfo(models.Model):
    USER_TYPE = (
        ('VEN', 'Vendedor'),
        ('CMA', 'Cliente Mayorista'),
        ('CMI', 'Cliente Minorista'),
        ('ADM', 'Administrador')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Cliente')
    user_type = models.CharField(max_length=3, choices=USER_TYPE, blank=True, null=True, verbose_name='Tipo de Usuario')
    related_name = models.CharField(max_length=120, verbose_name='Nombre')
    related_last_name = models.CharField(max_length=120, verbose_name='Apellido')
    related_customer_name = models.CharField(max_length=150, verbose_name='Nombre del Comercio')
    related_customer_address = models.CharField(max_length=150, verbose_name='Dirección del Comercio')
    related_telephone = models.CharField(blank=True, null=True, max_length=15, verbose_name='Teléfono')
    related_cel_phone = models.CharField(max_length=15, verbose_name='Celular')
    related_city = models.CharField(max_length=80, verbose_name='Localidad')
    related_zip_code = models.CharField(max_length=15, verbose_name='Código Postal')

    def email(self):
        return self.user.email

    email.short_description = 'Usuario'

    def __str__(self):
        return str(self.user.email)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


class CSVFilesData(models.Model):
    file = models.CharField(max_length=15, verbose_name='Archivo')
    modified_date = models.CharField(max_length=50, null=True, blank=True, verbose_name='Última modificación')

    def __str__(self):
        return str(self.file)

    class Meta:
        verbose_name = 'Archivos CSV'
        verbose_name_plural = 'Archivos CSV'
