from django.db import models

class Blok(models.Model):
    blok_id = models.CharField(max_length=10, primary_key=True)
    blok_adi = models.CharField(max_length=20)
    blok_onceligi = models.IntegerField()
    # Bölüm ilişkisi
    bolum = models.ForeignKey('Bolum', on_delete=models.CASCADE, related_name='bloklar')

    def __str__(self):
        return f"{self.blok_adi} ({self.blok_id})"

class Bolum(models.Model):
    bolum_id = models.CharField(max_length=10, primary_key=True)
    bolum_adi = models.CharField(max_length=50)

    def __str__(self):
        return self.bolum_adi

class Kullanici(models.Model):
    ROLES = (('ogretim_uyesi', 'Öğretim Üyesi'), ('editor', 'Editör'), ('asistan', 'Asistan'))
    kullanici_id = models.AutoField(primary_key=True)
    isim = models.CharField(max_length=50)
    isim2 = models.CharField(max_length=50, blank=True, null=True)
    mail = models.EmailField(unique=True)
    parola = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, choices=ROLES)

    def __str__(self):
        return self.isim

class Derslik(models.Model):
    derslik_id = models.CharField(max_length=10, primary_key=True)
    kod = models.CharField(max_length=20)
    kapasite = models.IntegerField()
    erisilebilirlik = models.BooleanField(default=False)
    oncelik = models.IntegerField()
    tur = models.CharField(max_length=20, choices=[('teorik', 'Teorik'), ('laboratuvar', 'Laboratuvar'), ('uygulama', 'Uygulama')])
    blok = models.ForeignKey(Blok, on_delete=models.CASCADE)
    laboratuvar_uygunlugu = models.BooleanField(default=False)

    def __str__(self):
        return self.kod

class Ders(models.Model):
    ders_id = models.CharField(max_length=10, primary_key=True)
    ders_kodu = models.CharField(max_length=20)
    ders_adi = models.CharField(max_length=50)
    ders_turu = models.CharField(max_length=20, choices=[('teorik', 'Teorik'), ('uygulama', 'Uygulama'), ('laboratuvar', 'Laboratuvar'), ('online', 'Online')])
    ogrenci_sayisi = models.IntegerField()
    bolum = models.ForeignKey(Bolum, on_delete=models.CASCADE)
    ogretmen = models.ForeignKey(Kullanici, on_delete=models.CASCADE, related_name='verdigi_dersler')
    oncelik_numarasi = models.IntegerField(default=3)
    ders_zamani = models.CharField(max_length=20, blank=True, null=True)
    ders_uzunlugu = models.IntegerField(default=1)  # Saat/dakika
    engelli_erişim_gerektiriyor = models.BooleanField(default=False)
    uygulama_lab_gerekli = models.BooleanField(default=False)
    sinif = models.IntegerField(choices=[(1, '1. Sınıf'), (2, '2. Sınıf'), (3, '3. Sınıf'), (4, '4. Sınıf')], default=1)

    def __str__(self):
        return self.ders_adi

class Zaman(models.Model):
    gun = models.CharField(max_length=10)
    saat = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.gun} {self.saat}"

class OzelDurum(models.Model):
    kullanici = models.ForeignKey(Kullanici, on_delete=models.CASCADE)
    ders = models.ForeignKey(Ders, on_delete=models.CASCADE, blank=True, null=True)
    gun = models.CharField(max_length=10)
    saat = models.CharField(max_length=5)
    aciklama = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.kullanici} - {self.gun} {self.saat}"

class DersProgrami(models.Model):
    ders = models.ForeignKey(Ders, on_delete=models.CASCADE)
    derslik = models.ForeignKey(Derslik, on_delete=models.CASCADE)
    bolum = models.ForeignKey(Bolum, on_delete=models.CASCADE)
    sorumlu = models.ForeignKey(Kullanici, on_delete=models.CASCADE)
    time = models.CharField(max_length=5)
    date = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.ders} @ {self.derslik} - {self.date} {self.time}"
