import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.widgets import AdminFileWidget
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django.forms import ModelForm
from django import forms
from django.db import models

from rest_framework.authtoken.models import Token
from allauth.account.models import EmailAddress
from import_export import resources

from app.models import UserInfo
from app.models import Customer
from app.models import ProductImages
from app.models import Products
from app.models import AccountBalance
from app.models import Invoices
from app.models import InvoiceItems
from app.models import OrderStatus
from app.models import PaymentMethods
from app.models import Order
from app.models import OrderItems
from app.models import CSVFilesData


# Unregister models
# admin.site.unregister(User)
admin.site.unregister(Token)
admin.site.unregister(EmailAddress)


# class UserCreateForm(ModelForm):
# 	email = forms.EmailField(required=True, label='Direccion de email')
#
# 	class Meta:
# 		model = User
# 		fields = ('email',)
#
#
# class UserInline(admin.StackedInline):
# 	model = UserInfo
# 	can_delete = False
# 	verbose_name = 'Cliente Las Marias'
# 	verbose_name_plural = 'Cliente Las Marias'
#
#
# class UserAdmin(BaseUserAdmin):
#     inlines = (UserInline, )
#     add_form = UserCreateForm
#
#     list_display = ('email', 'get_customer_id', 'get_customer', 'get_user_type',)
#     empty_value_display = ''
#
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email',)
#             }
#         ),
#     )
#
#     def get_customer(self, obj):
#         return obj.userinfo.customer_id.first_name + ' ' + obj.userinfo.customer_id.last_name
#
#     def get_customer_id(self, obj):
#         return obj.userinfo.customer_id
#
#     def get_user_type(self, obj):
#         return obj.userinfo.user_type
#
#     get_customer.short_description = 'Cliente'
#     get_customer_id.short_description = 'Código de Cliente'
#     get_user_type.short_description = 'Tipo de Usuario'


class UserInfoAdmin(admin.ModelAdmin):
	list_display = ('get_user_email', 'get_customer_id', 'customer_id', 'user_type', 'get_user_last_login', 'get_user_created',)
	list_filter = ('user__email', 'customer_id__customer_id', 'customer_id', 'user_type',)
	readonly_fields=('email', 'related_name', 'related_last_name', 'related_customer_name', 'related_telephone', 'related_cel_phone', 'related_customer_address', 'related_city', 'related_zip_code',)
	fieldsets = (
		(None, {
			'fields': ('email',),
		}),
		(None, {
			'fields': ('customer_id', 'user_type',),
		}),
		(None, {
			'fields': ('related_name', 'related_last_name', 'related_customer_name', 'related_telephone', 'related_cel_phone', 'related_customer_address', 'related_city', 'related_zip_code',)
		})
	)

	def get_user_email(self, obj):
		return obj.user.email

	def get_customer_id(self, obj):
		if obj.customer_id:
			return obj.customer_id.customer_id
		else:
			return None

	def get_user_created(self, obj):
		return obj.user.date_joined.strftime("%d/%m/%Y %H:%M")

	def get_user_last_login(self, obj):
		if obj.user.last_login:
			return obj.user.last_login.strftime("%d/%m/%Y %H:%M")

	get_user_email.short_description = 'Usuario'
	get_customer_id.short_description = 'Código de Cliente'
	get_user_created.short_description = 'Fecha de Alta'
	get_user_last_login.short_description = 'Último Ingreso'

	get_user_email.admin_order_field = 'email'

class CustomerAdmin(admin.ModelAdmin):
	list_display = ('customer_id', 'name', 'address', 'city', 'cuit', 'telephone', 'discount')
	list_filter = ('customer_id', 'name', 'city')


class ProductImagesWidget(AdminFileWidget):
	def render(self, name, value, attrs=None, renderer=None):
		output = []
		if value and getattr(value, "url", None):
			image_url = value.url
			file_name=str(value)
			output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" style="margin: 5px 0 25px 0; float: right;" /></a> %s ' % (image_url, image_url, file_name, _('')))
		output.append(super(AdminFileWidget, self).render(name, value, attrs))
		return mark_safe(u''.join(output))

class ProductImagesInline(admin.TabularInline):
	model = ProductImages
	# form = ProductImagesForm
	formfield_overrides = {models.ImageField: {'widget': ProductImagesWidget}}
	extra = 0
	verbose_name = 'Imágen del Producto'
	verbose_name_plural = 'Imágenes del Producto'

class ProductsAdmin(admin.ModelAdmin):
	inlines = (ProductImagesInline, )
	list_display = ('product_id', 'name', 'brand', 'product_line', 'unit', 'package', 'offer', 'get_price', 'get_offer_price')
	list_filter = ('name', 'brand', 'product_line', 'unit')

	def get_price(self, obj):
		return "$ {:,.2f}".format(obj.price)

	def get_offer_price(self, obj):
		return "$ {:,.2f}".format(obj.offer_price)

	get_price.short_description = 'Precio'
	get_offer_price.short_description = 'Precio Oferta'


class InvoiceItemsInline(admin.TabularInline):
	model = InvoiceItems
	verbose_name_plural = 'Productos'
	extra = 0


class InvoiceAdmin(admin.ModelAdmin):
	inlines = (InvoiceItemsInline, )
	list_display = ('invoice_id', 'get_customer_id', 'customer_id', 'date_format', 'get_iva_format', 'get_taxes_format', 'get_total_format')

	def get_customer_id(self, obj):
		return obj.customer_id.customer_id

	def get_total_format(self, obj):
		return "$ {:,.2f}".format(obj.get_total())
	
	def get_iva_format(self, obj):
		return "$ {:,.2f}".format(obj.iva)
	
	def get_taxes_format(self, obj):
		return "$ {:,.2f}".format(obj.taxes)
	
	def date_format(self, obj):
		return obj.date.strftime("%d/%m/%Y")

	get_customer_id.short_description = 'Código de Cliente'
	get_total_format.short_description = 'Total'
	get_iva_format.short_description = 'IVA'
	get_taxes_format.short_description = 'Percepciones'
	date_format.short_description = 'Fecha'

	date_format.admin_order_field = 'date'


class AccountBalanceAdmin(admin.ModelAdmin):
	list_display = ('get_customer_id', 'customer_id', 'voucher', 'date_format', 'get_balance')

	def get_customer_id(self, obj):
		return obj.customer_id.customer_id

	def get_balance(self, obj):
		return "$ {:,.2f}".format(obj.balance)
	
	def date_format(self, obj):
		return obj.date.strftime("%d/%m/%Y")

	get_customer_id.short_description = 'Código de Cliente'
	get_balance.short_description = 'Saldo'
	date_format.short_description = 'Fecha del Comprobante'

	date_format.admin_order_field = 'date'

class PaymentMethodsAdmin(admin.ModelAdmin):
	list_display = ('payment', 'sort')
	ordering = ('sort',)


class OrderStatusAdmin(admin.ModelAdmin):
	list_display = ('status', 'sort')
	ordering = ('sort',)


class OrderItemsInline(admin.TabularInline):
	model = OrderItems
	verbose_name_plural = 'Productos'
	extra = 0


class OrderAdmin(admin.ModelAdmin):
	inlines = (OrderItemsInline, )
	list_display = ('order_id', 'get_customer_id', 'customer_id', 'date_format', 'status', 'payment', 'shipping', 'get_total_format', 'email', 'download_link')
	list_filter = ('status', 'shipping', 'date', 'customer_id', 'payment')
	readonly_fields = ('email', 'download_link', 'created_at')
	fieldsets = (
		(None, {
			'fields': ('email',),
		}),
		(None, {
			'fields': ('customer_id',),
		}),
		(None, {
			'fields': ('date', 'status', 'payment', 'shipping',)
		}),
		(None, {
			'fields': ('download_link',)
		}),
		(None, {
			'fields': ('created_at',)
		})
	)

	def download_link(self, obj):
		return format_html('<a href="{}" style="color:#35B78F;border-bottom:1px solid #35B78F;">Exportar</a>', reverse('export-order', args=[obj.order_id]))

	def get_customer_id(self, obj):
		return obj.customer_id.customer_id

	def get_total_format(self, obj):
		return "$ {:,.2f}".format(obj.get_total())
	
	def date_format(self, obj):
		return obj.date.strftime("%d/%m/%Y")

	download_link.short_description = "CSV"
	get_customer_id.short_description = 'Nro Cliente'
	get_total_format.short_description = 'Total'
	date_format.short_description = 'Fecha'

	date_format.admin_order_field = 'date'


class TokenAdmin(admin.ModelAdmin):
	list_display = ('key', 'get_email', 'created')
	list_filter = ('user__email',)

	def get_email(self, obj):
		return obj.user.email

	get_email.short_description = 'Usuario'


class EmailAddressForm(ModelForm):

	class Meta:
		model = EmailAddress
		fields = ['email', 'verified']

class EmailAddressAdmin(admin.ModelAdmin):
	form = EmailAddressForm
	list_display = ('email', 'verified')
	list_filter = ('email', 'verified')
	fieldsets = (
		(None, {
			'fields': ('email', 'verified'),
		}),
	)
	readonly_fields=('email',)


class CSVFilesDataAdmin(admin.ModelAdmin):
	list_display = ('file', 'modified_date')


#Import-Export Resources
class CustomerResource(resources.ModelResource):

	class Meta:
		model = Customer
		import_id_fields = ('customer_id',)
		exclude = ('doc_type')
		skip_unchanged = True


class ProductsResource(resources.ModelResource):

	class Meta:
		model = Products
		import_id_fields = ('product_id',)
		skip_unchanged = True

	def before_import_row(self, row, **kwargs):
		if row['offer'] == 'N':
			row['offer'] = False
		elif row['offer'] == 'S':
			row['offer'] = True
		row['product_id'] = row['product_id'].strip()


class AccountBalanceResource(resources.ModelResource):

	class Meta:
		model = AccountBalance
		import_id_fields = ('customer_id', 'date', 'voucher',)
		skip_unchanged = True
	
	def before_import_row(self, row, **kwargs):
		row['date'] = datetime.datetime.strptime(row['date'], "%d/%m/%Y").strftime("%Y-%m-%d")


class InvoicesResource(resources.ModelResource):

	class Meta:
		model = Invoices
		import_id_fields = ('invoice_id','customer_id','invoice_type','invoice_branch','invoice_number','date','iva','taxes',)
		skip_unchanged = True
	
	def before_import_row(self, row, **kwargs):
		row['date'] = datetime.datetime.strptime(row['date'], "%d/%m/%Y").strftime("%Y-%m-%d")
		row['invoice_id'] = row['invoice_type'].strip() + '-' + str(row['invoice_branch'].strip()) + '-' + str(row['invoice_number'].strip())	


class InvoiceItemsResource(resources.ModelResource):

	class Meta:
		model = InvoiceItems
		import_id_fields = ('invoice_id','invoice_type','invoice_branch','invoice_number','product_id','product_description','price','quantity','amount',)
		skip_unchanged = True
	
	def before_import_row(self, row, **kwargs):
		row['invoice_id'] = row['invoice_type'].strip() + '-' + str(row['invoice_branch'].strip()) + '-' + str(row['invoice_number'].strip())	


class OrderResource(resources.ModelResource):

	class Meta:
		model = OrderItems
		fields = ('order_id', 'order_id__customer_id', 'order_id__date', 'order_id__payment', 'order_id__shipping', 'product_id', 'quantity', 'price')
		export_order = ('order_id', 'order_id__customer_id', 'order_id__date', 'order_id__payment', 'order_id__shipping', 'product_id', 'quantity', 'price')


# admin.site.register(User, UserAdmin)
admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(Customer, CustomerAdmin)
# admin.site.register(ProductImages)
admin.site.register(Products, ProductsAdmin)
admin.site.register(AccountBalance, AccountBalanceAdmin)
admin.site.register(Invoices, InvoiceAdmin)
admin.site.register(OrderStatus, OrderStatusAdmin)
admin.site.register(PaymentMethods, PaymentMethodsAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Token, TokenAdmin)
admin.site.register(EmailAddress, EmailAddressAdmin)
admin.site.register(CSVFilesData, CSVFilesDataAdmin)
