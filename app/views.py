import requests

from django.db import IntegrityError

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_auth.views import LoginView

from allauth.account.models import EmailConfirmation, EmailAddress

from django.contrib.auth.models import User
from app.models import UserInfo
from app.models import Customer
from app.models import Products
from app.models import AccountBalance
from app.models import Invoices
from app.models import Order
from app.models import OrderItems
from app.models import CSVFilesData

from app.serializers import CustomerSerializer
from app.serializers import ProductSerializer
from app.serializers import AccountBalanceSerializer
from app.serializers import InvoiceSerializer
from app.serializers import OrderSerializer
from app.serializers import EmailConfirmationSerializer

from app.permissions import SellerPermission
from app.permissions import HasPermissionOrSeller

from app.admin import OrderResource

class CustomerList(generics.ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (IsAuthenticated, SellerPermission,)


class CustomerDetail(generics.ListAPIView):
    serializer_class = CustomerSerializer
    permission_classes = (IsAuthenticated, HasPermissionOrSeller)

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return Customer.objects.filter(customer_id=customer_id)


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
    permission_classes = (IsAuthenticated, SellerPermission,)

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return AccountBalance.objects.filter(customer_id=customer_id).order_by('date', 'voucher')


class InvoiceList(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = (IsAuthenticated, HasPermissionOrSeller)

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return Invoices.objects.filter(customer_id=customer_id)


class InvoiceDetail(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = (IsAuthenticated, HasPermissionOrSeller)

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        invoice_number = self.kwargs['invoice_number']
        return Invoices.objects.filter(customer_id=customer_id, number=invoice_number)


class OrderList(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, HasPermissionOrSeller)

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return Order.objects.filter(customer_id=customer_id)

    def perform_create(self, serializer):
        # Get current user
        req = serializer.context['request']
        customer_id = self.kwargs['customer_id']
        customer = Customer.objects.get(customer_id=customer_id)
        serializer.save(user_id=req.user, customer_id=customer)
    
    def create(self, request, *args, **kwargs):
        try:
            return super(generics.ListCreateAPIView, self).create(request, *args, **kwargs)
        except IntegrityError as e:
            if 'Duplicate entry' in e.args[1]:
                content = {'error': 'Pedido duplicado'}
                return Response(content, status=status.HTTP_409_CONFLICT)
            else:
                content = {'error': 'IntegrityError'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, HasPermissionOrSeller)
    lookup_field = 'order_id'

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        order_id = self.kwargs['order_id']
        return Order.objects.filter(customer_id=customer_id, order_id=order_id)


class CustomLoginView(LoginView):
    def get_response(self):
        original_response = super().get_response()
        user_type = self.user.userinfo.user_type
        user_name = self.user.userinfo.related_name
        user_last_name = self.user.userinfo.related_last_name
        email = self.user.email
        my_data = {'user_type': user_type, 'name': user_name, 'last_name': user_last_name, 'email': email}
        original_response.data.update(my_data)
        return original_response


@api_view(['POST'])
def SendConfirmEmail(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = EmailConfirmationSerializer(data=data)
        if serializer.is_valid():
            data = serializer.data
            try:
                email = EmailAddress.objects.get(email=data['email'])
                if email.verified == False:
                    email_confirmation = EmailConfirmation.create(email)
                    email_confirmation.send()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error':'cuenta ya verificada'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            except ObjectDoesNotExist:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def ConfirmEmail(request, key):
    current_site = get_current_site(request)
    domain = current_site.domain
    r = requests.post('http://'+domain+'/rest-auth/registration/verify-email/', {'key':key})
    context = {'result': r}
    return render(request, 'confirm_email.html', context)


@staff_member_required
def ExportOrder(request, order_id):
    order_resource = OrderResource()
    queryset = OrderItems.objects.filter(order_id=order_id)
    dataset = order_resource.export(queryset)
    response = HttpResponse(dataset.csv, content_type='text/csv')
    file_name = 'pedido-'+str(order_id)+'.csv'
    response['Content-Disposition'] = "attachment; filename='%s'" % file_name
    return response


# PubNub pusblish message test view
def PublishMessage(request):
    pnconfig = PNConfiguration()
    pnconfig.publish_key = settings.PUBNUB_PUBLISH_KEY
    pnconfig.subscribe_key = settings.PUBNUB_SUBSCRIBE_KEY
    pnconfig.ssl = False
    
    pubnub = PubNub(pnconfig)

    def publish_callback(result, status):
        print(result)
        print(status)
        # Handle PNPublishResult and PNStatus
 
    try:
        publish_data = list(CSVFilesData.objects.filter(Q(file='Productos') | Q(file='Clientes')).values('file', 'modified_date'))
        pubnub.publish().channel('lasmarias').message(publish_data).pn_async(publish_callback)
    except PubNubException as e:
        print(e)
    
    
    html = "<html><body><h1>Mensaje enviado.</h1></body></html>"
    return HttpResponse(html)