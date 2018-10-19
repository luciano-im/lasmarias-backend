from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from  django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from app.models import UserInfo


@receiver(pre_save, sender=UserInfo, dispatch_uid='app.signals.preSave_UserInfo')
def preSave_UserInfo(sender, instance, **kwargs):
    # Check if is a new user
    try:
        userinfo = UserInfo.objects.get(id=instance.pk)
        if userinfo.customer_id_id is None and instance.customer_id_id is not None:
            print('ENVIAR EMAIL')
    except ObjectDoesNotExist:
        if instance.customer_id_id is not None:
            print('ENVIAR EMAIL')
