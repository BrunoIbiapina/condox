from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        MORADOR = 'MORADOR', 'Morador'
        PORTEIRO = 'PORTEIRO', 'Porteiro'
        GESTOR = 'GESTOR', 'Gestor/Síndico'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MORADOR)

    def is_morador(self): return self.role == self.Role.MORADOR
    def is_porteiro(self): return self.role == self.Role.PORTEIRO
    def is_gestor(self):   return self.role == self.Role.GESTOR