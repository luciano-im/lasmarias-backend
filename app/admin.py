from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

from django.forms import ModelForm
from django import forms

from app.models import UserInfo
from app.models import Customer
from app.models import Products
from app.models import AccountBalance
from app.models import Invoices
from app.models import InvoiceItems
from app.models import OrderStatus
from app.models import PaymentMethods
from app.models import Order
from app.models import OrderItems


# Unregister models
# admin.site.unregister(User)


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
	list_display = ('get_user_email', 'get_customer_id', 'customer_id', 'user_type', 'get_user_last_login', 'get_user_created')
	fieldsets = (
		(None, {
			'fields': ('email',),
		}),
		(None, {
			'fields': ('customer_id', 'user_type',),
		}),
	)
	readonly_fields=('email',)

	def get_user_email(self, obj):
		return obj.user.email

	def get_customer_id(self, obj):
		return obj.customer_id.customer_id

	def get_user_created(self, obj):
		return obj.user.date_joined

	def get_user_last_login(self, obj):
		return obj.user.last_login

	get_user_email.short_description = 'Usuario'
	get_customer_id.short_description = 'Código de Cliente'
	get_user_created.short_description = 'Fecha de Alta'
	get_user_last_login.short_description = 'Último Ingreso'


class CustomerAdmin(admin.ModelAdmin):
	list_display = ('customer_id', 'first_name', 'last_name', 'zip_code', 'cuit', 'telephone', 'get_discount')

	def get_discount(self, obj):
		return "%s %%" % obj.discount

	get_discount.short_description = 'Descuento'


class ProductsAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'brand', 'product_line', 'unit', 'get_price')

	def get_price(self, obj):
		return "$ %s" % obj.price

	get_price.short_description = 'Precio'


class InvoiceItemsInline(admin.TabularInline):
	model = InvoiceItems
	verbose_name_plural = 'Productos'
	extra = 1


class InvoiceAdmin(admin.ModelAdmin):
	inlines = (InvoiceItemsInline, )
	list_display = ('number', 'get_customer_id', 'customer_id', 'date', 'get_total_format')

	def get_customer_id(self, obj):
		return obj.customer_id.customer_id

	def get_total_format(self, obj):
		return "$ %s" % obj.get_total()

	get_customer_id.short_description = 'Código de Cliente'
	get_total_format.short_description = 'Total'


class AccountBalanceAdmin(admin.ModelAdmin):
	list_display = ('get_customer_id', 'customer_id', 'get_balance')

	def get_customer_id(self, obj):
		return obj.customer_id.customer_id

	def get_balance(self, obj):
		return "$ %s" % obj.balance

	get_customer_id.short_description = 'Código de Cliente'
	get_balance.short_description = 'Saldo'


class PaymentMethodsAdmin(admin.ModelAdmin):
	list_display = ('payment', 'sort')
	ordering = ('sort',)


class OrderStatusAdmin(admin.ModelAdmin):
	list_display = ('status', 'sort')
	ordering = ('sort',)


class OrderItemsInline(admin.TabularInline):
	model = OrderItems
	verbose_name_plural = 'Productos'
	extra = 1


class OrderAdmin(admin.ModelAdmin):
	inlines = (OrderItemsInline, )
	list_display = ('order_id', 'user_id', 'get_customer_id', 'customer_id', 'date', 'status', 'payment', 'shipping', 'get_total_format')

	def get_customer_id(self, obj):
		return obj.customer_id.customer_id

	def get_total_format(self, obj):
		return "$ %s" % obj.get_total()

	get_customer_id.short_description = 'Código de Cliente'
	get_total_format.short_description = 'Total'


# admin.site.register(User, UserAdmin)
admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Products, ProductsAdmin)
admin.site.register(AccountBalance, AccountBalanceAdmin)
admin.site.register(Invoices, InvoiceAdmin)
admin.site.register(OrderStatus, OrderStatusAdmin)
admin.site.register(PaymentMethods, PaymentMethodsAdmin)
admin.site.register(Order, OrderAdmin)
