from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer

from app.models import UserInfo
from app.models import Customer
from app.models import Products
from app.models import ProductImages
from app.models import AccountBalance
from app.models import InvoiceItems
from app.models import Invoices
from app.models import OrderItems
from app.models import Order


class ProfileRegisterSerializer(RegisterSerializer):
    related_name = serializers.CharField(max_length=120, source="userinfo.related_name")
    related_last_name = serializers.CharField(max_length=120, source="userinfo.related_last_name")
    related_customer_name = serializers.CharField(max_length=150, source="userinfo.related_customer_name")
    related_customer_address = serializers.CharField(max_length=150, source="userinfo.related_customer_address")
    related_telephone = serializers.CharField(required=False, default='', max_length=15, source="userinfo.related_telephone")
    related_cel_phone = serializers.CharField(max_length=15, source="userinfo.related_cel_phone")
    related_city = serializers.CharField(max_length=80, source="userinfo.related_city")
    related_zip_code = serializers.CharField(max_length=15, source="userinfo.related_zip_code")

    def custom_signup(self, request, user):
        profile_data = self.validated_data['userinfo']
        profile = UserInfo.objects.create(user=user)
        profile.related_name = profile_data['related_name']
        profile.related_last_name = profile_data['related_last_name']
        profile.related_customer_name = profile_data['related_customer_name']
        profile.related_customer_address = profile_data['related_customer_address']
        profile.related_telephone = profile_data['related_telephone']
        profile.related_cel_phone = profile_data['related_cel_phone']
        profile.related_city = profile_data['related_city']
        profile.related_zip_code = profile_data['related_zip_code']
        profile.save()


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ('related_name', 'related_last_name', 'related_customer_name', 'related_customer_address', 'related_telephone', 'related_cel_phone', 'related_city', 'related_zip_code')


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('customer_id', 'cuit', 'name', 'address', 'city', 'telephone', 'discount')


class ProductImagesSerializer(serializers.ModelSerializer):
    image_relative_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImages
        fields = ('image_relative_url',)
    
    # Get relative path
    def get_image_relative_url(self, obj):
        return obj.image.url


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImagesSerializer(many=True)

    class Meta:
        model = Products
        fields = ('product_id', 'name', 'brand', 'product_line', 'unit', 'price', 'offer', 'offer_price', 'package', 'images',)


class AccountBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountBalance
        fields = ('voucher', 'date', 'balance')


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
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', input_formats=['%Y-%m-%dT%H:%M:%S'])
    items = OrderItemsSerializer(many=True)

    class Meta:
        model = Order
        fields = ('order_id', 'user_id', 'customer_id', 'status', 'payment', 'date', 'discount', 'shipping', 'created_at', 'items')
        read_only_fields = ('user_id', 'customer_id')
    
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
        instance.created_at = validated_data.get('created_at', instance.created_at)
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
