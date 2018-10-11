from rest_framework import serializers

from app.models import Customer
from app.models import Products

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('customer_id', 'cuit', 'first_name', 'last_name', 'zip_code', 'telephone', 'discount')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ('id', 'name', 'brand', 'product_line', 'unit', 'price')
