from django.contrib import admin
from .models import Evento, Foto

class FotoInline(admin.TabularInline):
    model = Foto
    extra = 1

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo','condominio','data')
    list_filter = ('condominio','data')
    inlines = [FotoInline]