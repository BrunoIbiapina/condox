from django.db import models
from django.conf import settings
from condominios.models import Condominio

class Aviso(models.Model):
    condominio = models.ForeignKey(Condominio, on_delete=models.CASCADE, related_name='avisos')
    titulo = models.CharField(max_length=150)
    mensagem = models.TextField()
    anexos = models.FileField(upload_to='avisos/', blank=True, null=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['-criado_em']
    def __str__(self): return f"{self.titulo} ({self.condominio})"