from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

from django.forms import ModelForm
from django import forms

from app.models import UserInfo


# Unregister models
admin.site.unregister(User)


class UserCreateForm(ModelForm):
	email = forms.EmailField(required=True, label='Direccion de email')

	class Meta:
		model = User
		fields = ('email',)

class UserInline(admin.StackedInline):
	model = UserInfo
	can_delete = False
	verbose_name = 'Cliente Las Marias'
	verbose_name_plural = 'Cliente Las Marias'
	# exclude = ('account_confirmed', 'random_password', 'is_commercial')


class UserAdmin(BaseUserAdmin):
    inlines = (UserInline, )
    add_form = UserCreateForm

    list_display = ('email', 'get_customer_id', 'get_customer', 'get_user_type',)
    empty_value_display = ''

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email',)
            }
        ),
    )

    def get_customer(self, obj):
        return obj.userinfo.customer.first_name

    def get_customer_id(self, obj):
        return obj.userinfo.customer_id

    def get_user_type(self, obj):
        return obj.userinfo.user_type

    get_customer.short_description = 'Cliente'
    get_customer_id.short_description = 'Código de Cliente'
    get_user_type.short_description = 'Tipo de Usuario'




admin.site.register(User, UserAdmin)
