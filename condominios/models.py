from django.db import models
from django.conf import settings

class Condominio(models.Model):
    nome = models.CharField(max_length=120)
    endereco = models.CharField(max_length=255, blank=True)
    def __str__(self): return self.nome

class Bloco(models.Model):
    condominio = models.ForeignKey(Condominio, on_delete=models.CASCADE, related_name='blocos')
    nome = models.CharField(max_length=50)
    class Meta: unique_together = ('condominio','nome')
    def __str__(self): return f"{self.condominio} - Bloco {self.nome}"

class Unidade(models.Model):
    condominio = models.ForeignKey(Condominio, on_delete=models.CASCADE, related_name='unidades')
    bloco = models.ForeignKey(Bloco, on_delete=models.SET_NULL, null=True, blank=True, related_name='unidades')
    numero = models.CharField(max_length=20)
    morador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='unidades')
    class Meta: unique_together = ('condominio','bloco','numero')
    def __str__(self):
        label_bloco = self.bloco.nome if self.bloco else 'Sem Bloco'
        return f"{self.condominio} - {label_bloco} - Unidade {self.numero}"