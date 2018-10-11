from rest_framework import serializers

from app.models import Customer
from app.models import Products
from app.models import AccountBalance
from app.models import InvoiceItems
from app.models import Invoices


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('customer_id', 'cuit', 'first_name', 'last_name', 'zip_code', 'telephone', 'discount')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ('id', 'name', 'brand', 'product_line', 'unit', 'price')


class AccountBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountBalance
        fields = ('customer_id', 'balance')


class InvoiceItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItems
        fields = ('product_id', 'price', 'quantity')


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemsSerializer(many=True, read_only=True)

    class Meta:
        model = Invoices
        fields = ('number', 'customer_id', 'date', 'items')
