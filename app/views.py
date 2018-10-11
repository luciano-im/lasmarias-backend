from django.shortcuts import render

from rest_framework import generics

from app.models import Customer
from app.models import Products
from app.models import AccountBalance

from app.serializers import CustomerSerializer
from app.serializers import ProductSerializer
from app.serializers import AccountBalanceSerializer

class CustomerList(generics.ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    #permission_classes = (IsAdminUser,)
    #authentication_classes = (authentication.TokenAuthentication,)


class CustomerDetail(generics.ListAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Customer.objects.filter(customer_id=user_id)


class ProductList(generics.ListAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer


class ProductDetail(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Products.objects.filter(id=product_id)


class AcountBalanceDetail(generics.ListAPIView):
    serializer_class = AccountBalanceSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return AccountBalance.objects.filter(customer_id=user_id)
