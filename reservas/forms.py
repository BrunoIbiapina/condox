from django import forms
from .models import Reserva

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['area', 'inicio', 'fim', 'observacoes']
        widgets = {
            'inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fim': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # morador sempre o usuário logado (não expõe no form)
        self.user = user