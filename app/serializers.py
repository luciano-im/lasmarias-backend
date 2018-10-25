from rest_framework import serializers

from app.models import Customer
from app.models import Products
from app.models import AccountBalance
from app.models import InvoiceItems
from app.models import Invoices
from app.models import OrderItems
from app.models import Order


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


class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = ('product_id', 'price', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemsSerializer(many=True)

    class Meta:
        model = Order
        fields = ('order_id', 'user_id', 'customer_id', 'status', 'payment', 'date', 'discount', 'shipping', 'items')

    def create(self, validated_data):
        items = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item in items:
            OrderItems.objects.create(order_id=order, **item)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        items = (instance.items).all()
        items = list(items)
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.customer_id = validated_data.get('customer_id', instance.customer_id)
        instance.status = validated_data.get('status', instance.status)
        instance.payment = validated_data.get('payment', instance.payment)
        instance.date = validated_data.get('date', instance.date)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.shipping = validated_data.get('shipping', instance.shipping)
        instance.save()

        for item_data in items_data:
            item = items.pop(0)
            item.product_id = item_data.get('product_id', item.product_id)
            item.price = item_data.get('price', item.price)
            item.quantity = item_data.get('quantity', item.quantity)
            item.save()
        return instance


class EmailConfirmationSerializer(serializers.Serializer):
    email = serializers.EmailField()
