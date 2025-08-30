from django.contrib import admin
from .models import Aviso

@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('titulo','condominio','criado_por','criado_em')
    list_filter = ('condominio',)
    search_fields = ('titulo','mensagem')