import requests
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from app.models import UserInfo
from allauth.account.models import EmailConfirmation, EmailAddress


@receiver(pre_save, sender=User, dispatch_uid='app.signals.preSave_User')
def preSave_User(sender, instance, **kwargs):
    # If it's a new user mark account as inactive to prevent sending email verification
    if not instance.pk:
        instance.is_active = False


@receiver(post_save, sender=User, dispatch_uid='app.signals.postSave_User')
def postSave_User(sender, instance, created, **kwargs):
    # If it's a new user and it's not staff member
    if created == True and not instance.is_staff:
        # Create UserInfo
        profile = UserInfo.objects.create(user=instance)
        profile.save()
        # send an email to the administrator
        requests.post(
            settings.EMAIL_URL,
            auth=('api', settings.EMAIL_KEY),
            data={
                'from': 'Nuevo Usuario Las Marias' + '<' + instance.email + '>',
                'to': ['luciano@lbartevisual.com.ar'],
                'subject': 'Nuevo Usuario en Las Marias App',
                'text': 'Se ha registrado un nuevo usuario en la aplicación de Las Marias con el email ' + instance.email
            }
        )


@receiver(pre_save, sender=UserInfo, dispatch_uid='app.signals.preSave_UserInfo')
def preSave_UserInfo(sender, instance, **kwargs):
    # Check if there is EmailAddress created, because this signal is fired after profile is created
    # in User post_save
    try:
        email = EmailAddress.objects.get(email=instance.user.email)
        email_confirmation = EmailConfirmation.create(email)
        # Check if needs to send email
        try:
            userinfo = UserInfo.objects.get(id=instance.pk)
            if userinfo.customer_id_id is None and instance.customer_id_id is not None:
                email_confirmation.send()
        except ObjectDoesNotExist:
            if instance.customer_id_id is not None:
                email_confirmation.send()
    except ObjectDoesNotExist:
        pass


@receiver(post_save, sender=UserInfo, dispatch_uid='app.signals.postSave_UserInfo')
def postSave_UserInfo(sender, instance, created, **kwargs):
    # If user type is administrator
    if instance.user_type == 'ADM':
        user = User.objects.get(email=instance.user.email)
        user.is_staff = True
        user.save()
    else:
        user = User.objects.get(email=instance.user.email)
        if user.is_staff == True:
            user.is_staff = False
            user.save()
