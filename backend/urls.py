"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView

# from app.views import SaveUserInfo
from app.views import CustomerList, CustomerDetail
from app.views import ProductList, ProductDetail
from app.views import AcountBalanceDetail
from app.views import InvoiceList, InvoiceDetail
from app.views import OrderList, OrderDetail
from app.views import ConfirmEmail
from app.views import SendConfirmEmail
from app.views import ExportOrder
from app.views import CustomLoginView
from app.views import PublishMessage

from allauth.account.views import AccountInactiveView

urlpatterns = [
    path('admin/', admin.site.urls),

    #re_path(r'^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', TemplateView.as_view(),  name='password_reset_confirm'),
    # re_path(r'^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$', TemplateView.as_view(), name="account_reset_password_from_key"),
    # Signal put new user as inactive, and allauth needs this url for reverse redirection
    # path('inactive/', AccountInactiveView.as_view(), name='account_inactive'),
    # Include allauth urls to prevent errors with reverse redirection of some urls like password reset and inactive account
    path('accounts/', include('allauth.urls')),
    
    # Custom Login view
    path('rest-auth/login/', CustomLoginView.as_view()),
    path('rest-auth/', include('rest_auth.urls')),
    re_path(r"^rest-auth/registration/account-confirm-email/(?P<key>[\s\d\w().+-_',:&]+)/$", ConfirmEmail, name="account_confirm_email"),
    path('rest-auth/registration/send-account-confirm-email/', SendConfirmEmail, name="send_account_confirm_email"),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('api/customer/', CustomerList.as_view()),
    path('api/customer/<customer_id>/', CustomerDetail.as_view()),
    path('api/product/', ProductList.as_view()),
    path('api/product/<product_id>/', ProductDetail.as_view()),
    path('api/balance/<customer_id>/', AcountBalanceDetail.as_view()),
    path('api/invoice/', InvoiceList.as_view()),
    path('api/invoice/<customer_id>/', InvoiceList.as_view()),
    path('api/invoice/<date_from>/<date_to>/', InvoiceList.as_view()),
    path('api/invoice/<customer_id>/<date_from>/<date_to>/', InvoiceList.as_view()),
    path('api/invoice-detail/<customer_id>/<invoice_id>/', InvoiceDetail.as_view()),
    path('api/order/<customer_id>/', OrderList.as_view()),
    path('api/order/<customer_id>/<order_id>/', OrderDetail.as_view()),

    path('export-order/<order_id>/', ExportOrder, name='export-order'),

    # PubNub publish test URL
    path('publish/', PublishMessage),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)