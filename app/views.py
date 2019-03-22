import requests

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

from app.serializers import UserInfoSerializer
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
    permission_classes = (IsAuthenticated, SellerPermission,)

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return AccountBalance.objects.filter(customer_id=user_id).order_by('date', 'voucher')


class InvoiceList(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = (IsAuthenticated, HasPermissionOrSeller)

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Invoices.objects.filter(customer_id=user_id)


class InvoiceDetail(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = (IsAuthenticated, HasPermissionOrSeller)

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        invoice_number = self.kwargs['invoice_number']
        return Invoices.objects.filter(customer_id=user_id, number=invoice_number)


class OrderList(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, HasPermissionOrSeller)

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Order.objects.filter(customer_id=user_id)


class OrderDetail(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, HasPermissionOrSeller)
    lookup_field = 'order_id'

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        order_id = self.kwargs['order_id']
        return Order.objects.filter(customer_id=user_id, order_id=order_id)


@api_view(['POST'])
def SaveUserInfo(request):
    if request.method == 'POST':
        # data = JSONParser().parse(request)
        data = request.data
        email = data['email']
        serializer = UserInfoSerializer(data=data)
        if serializer.is_valid():
            data = serializer.data
            user = User.objects.get(email=email)
            profile = UserInfo.objects.get(user_id=user.pk)
            
            profile.related_name = data['related_name']
            profile.related_last_name = data['related_last_name']
            profile.related_customer_name = data['related_customer_name']
            profile.related_customer_address = data['related_customer_address']
            profile.related_telephone = data['related_telephone']
            profile.related_cel_phone = data['related_cel_phone']
            profile.related_city = data['related_city']
            profile.related_zip_code = data['related_zip_code']
            profile.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    print("Confirmacion Email")
    current_site = get_current_site(request)
    domain = current_site.domain
    r = requests.post('http://'+domain+'/rest-auth/registration/verify-email/', {'key':key})
    if r.status_code == 200:
        html = "<html><body><h1>¡ Su cuenta ha sido activada !</h1></body></html>"
        return HttpResponse(html)
    else:
        html = "<html><body><h1>No hemos podido activar su cuenta, por favor intentelo nuevamente.</h1><p>Si continúa recibiendo este mensaje, por favor pongase en contacto con Las Marias para resolver el inconveniente a la menor brevedad posible.</p></body></html>"
        return HttpResponse(html)


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