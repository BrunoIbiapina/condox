from django.db import models
from condominios.models import Condominio

class Evento(models.Model):
    condominio = models.ForeignKey(Condominio, on_delete=models.CASCADE, related_name='eventos')
    titulo = models.CharField(max_length=150)
    data = models.DateField()
    descricao = models.TextField(blank=True)
    def __str__(self): return f"{self.titulo} ({self.data:%d/%m/%Y})"

class Foto(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField(upload_to='eventos/')
    legenda = models.CharField(max_length=120, blank=True)
    def __str__(self): return self.legenda or f"Foto {self.id}"