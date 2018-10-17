from django.shortcuts import render

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from app.models import Customer
from app.models import Products
from app.models import AccountBalance
from app.models import Invoices
from app.models import Order

from app.serializers import CustomerSerializer
from app.serializers import ProductSerializer
from app.serializers import AccountBalanceSerializer
from app.serializers import InvoiceSerializer
from app.serializers import OrderSerializer


class CustomerList(generics.ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (IsAuthenticated,)


class CustomerDetail(generics.ListAPIView):
    serializer_class = CustomerSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Customer.objects.filter(customer_id=user_id)


class ProductList(generics.ListAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)


class ProductDetail(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Products.objects.filter(id=product_id)


class AcountBalanceDetail(generics.ListAPIView):
    serializer_class = AccountBalanceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return AccountBalance.objects.filter(customer_id=user_id)


class InvoiceList(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Invoices.objects.filter(customer_id=user_id)


class InvoiceDetail(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        invoice_number = self.kwargs['invoice_number']
        return Invoices.objects.filter(customer_id=user_id, number=invoice_number)


class OrderList(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Order.objects.filter(customer_id=user_id)


class OrderDetail(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'order_id'

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        order_id = self.kwargs['order_id']
        return Order.objects.filter(customer_id=user_id, order_id=order_id)
