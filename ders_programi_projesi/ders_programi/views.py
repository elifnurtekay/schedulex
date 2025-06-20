from django.shortcuts import render, redirect
from .forms import DersForm, DerslikForm, ZamanForm, OzelDurumForm
from .models import Ders, Derslik, Zaman, OzelDurum, DersProgrami
from .utils import ders_programi_olustur
from .forms import DerslikForm
from .utils import bitis_saati_hesapla
from .utils import ders_programi_olustur_siniflara_gore
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'index.html')

def ders_list(request):
    dersler = Ders.objects.all()
    return render(request, 'ders_list.html', {'dersler': dersler})

def ders_ekle(request):
    if request.method == 'POST':
        form = DersForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ders_list')
    else:
        form = DersForm()
    return render(request, 'ders_ekle.html', {'form': form})

@login_required
def program_olustur(request):
    if request.method == 'POST':
        DersProgrami.objects.all().delete() #öndeki programı silmek
        atamalar = ders_programi_olustur()
        return render(request, 'program_sonuc.html', {'atamalar': atamalar})
    return render(request, 'program_olustur.html')


def program_goruntule(request):
    program = DersProgrami.objects.select_related('ders', 'derslik', 'sorumlu').all()
    # Programdaki her kayda bitiş saatini ekle
    for p in program:
        p.bitis_saati = bitis_saati_hesapla(p.time, p.ders.ders_uzunlugu)
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
    # Kullanılan saatleri sırala veya sabit belirle
    saatler = sorted(set(z.saat for z in Zaman.objects.all()))
    return render(request, "program_goruntule.html", {
        "program": program,
        "gunler": gunler,
        "saatler": saatler,
    })



def derslik_ekle(request):
    if request.method == 'POST':
        form = DerslikForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('derslik_list')
    else:
        form = DerslikForm()
    return render(request, 'derslik_ekle.html', {'form': form})

def derslik_list(request):
    derslikler = Derslik.objects.all()
    return render(request, 'derslik_list.html', {'derslikler': derslikler})


def program_goruntule_sinif(request):
    programlar = DersProgrami.objects.select_related('ders', 'derslik', 'sorumlu').all()
    siniflar = Ders.objects.values_list('sinif', flat=True).distinct().order_by('sinif')
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
    saatler = sorted(set(z.saat for z in Zaman.objects.all()))
    sinif_programlari = {}
    for sinif in siniflar:
        sinif_programlari[sinif] = programlar.filter(ders__sinif=sinif)
    return render(request, "program_goruntule_sinif.html", {
        "sinif_programlari": sinif_programlari,
        "gunler": gunler,
        "saatler": saatler,
        "siniflar": siniflar,
    })
