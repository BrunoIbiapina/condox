from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps

ROLE_PERMS = {
    'GESTOR': {
        'reservas': ['add', 'change', 'delete', 'view'],
        'financeiro': ['add', 'change', 'delete', 'view'],
        'comunicados': ['add', 'change', 'delete', 'view'],
        'galeria': ['add', 'change', 'delete', 'view'],
        'condominios': ['add', 'change', 'delete', 'view'],
    },
    'PORTEIRO': {
        'reservas': ['view', 'change'],
        'comunicados': ['view'],
        'galeria': ['view'],
    },
    'MORADOR': {
        'reservas': ['add', 'view'],
        'comunicados': ['view'],
        'galeria': ['view'],
        'financeiro': ['view'],
    },
}

class Command(BaseCommand):
    help = 'Cria grupos e atribui permissões por papel.'

    def handle(self, *args, **kwargs):
        for role, app_perms in ROLE_PERMS.items():
            group, _ = Group.objects.get_or_create(name=role)
            perms_to_set = []
            for app_label, actions in app_perms.items():
                for model in apps.get_app_config(app_label).get_models():
                    for act in actions:
                        codename = f"{act}_{model._meta.model_name}"
                        try:
                            perm = Permission.objects.get(
                                codename=codename,
                                content_type__app_label=app_label
                            )
                            perms_to_set.append(perm)
                        except Permission.DoesNotExist:
                            continue
            group.permissions.set(perms_to_set)
            self.stdout.write(self.style.SUCCESS(f"Grupo {role} configurado."))