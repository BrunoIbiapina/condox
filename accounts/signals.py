from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import User

@receiver(post_save, sender=User)
def sync_user_group(sender, instance: User, created, **kwargs):
    if not instance.role:
        return
    try:
        group = Group.objects.get(name=instance.role)
    except Group.DoesNotExist:
        return
    # remove de outros grupos de papel e adiciona no correto
    for g in Group.objects.filter(name__in=['GESTOR','PORTEIRO','MORADOR']):
        instance.groups.remove(g)
    instance.groups.add(group)