from django import forms
from .models import Ders, Derslik, Zaman, OzelDurum

class DersForm(forms.ModelForm):
    class Meta:
        model = Ders
        fields = '__all__'

class DerslikForm(forms.ModelForm):
    class Meta:
        model = Derslik
        fields = '__all__'

class ZamanForm(forms.ModelForm):
    class Meta:
        model = Zaman
        fields = '__all__'

class OzelDurumForm(forms.ModelForm):
    class Meta:
        model = OzelDurum
        fields = '__all__'
