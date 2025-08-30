from django.contrib import admin
from .models import Condominio, Bloco, Unidade

@admin.register(Condominio)
class CondominioAdmin(admin.ModelAdmin):
    search_fields = ('nome',)

@admin.register(Bloco)
class BlocoAdmin(admin.ModelAdmin):
    list_display = ('nome','condominio')
    list_filter = ('condominio',)

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('numero','bloco','condominio','morador')
    list_filter = ('condominio','bloco')
    search_fields = ('numero',)