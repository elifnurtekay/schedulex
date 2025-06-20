from .models import Ders, Derslik, Zaman, OzelDurum, DersProgrami
from datetime import datetime, timedelta

HATA_PAYI = 5

def atama_puani(ders, derslik, zaman):
    puan = 0

    # Kapasite tam uygunsa yüksek puan, hafif aşımda az puan
    if ders.ogrenci_sayisi <= derslik.kapasite:
        puan += 20
    elif ders.ogrenci_sayisi <= derslik.kapasite + HATA_PAYI:
        puan += 10
    else:
        return -100  # İmkansız

    # Engelli erişimi gerekiyorsa ve uygun ise puan
    if ders.engelli_erişim_gerektiriyor:
        if derslik.erisilebilirlik:
            puan += 10
        else:
            return -100

    # Laboratuvar/uygulamalı ders gereksinimi
    if ders.ders_turu in ["uygulama", "laboratuvar"]:
        if derslik.laboratuvar_uygunlugu:
            puan += 10
        else:
            return -100

    # Ders türü ile derslik türü uyumu (teorik/lab/uygulama)
    if ders.ders_turu == derslik.tur:
        puan += 8

    # Aynı bölümün blokunda ise ekstra puan
    if hasattr(ders, "bolum") and hasattr(derslik, "blok") and derslik.blok.bolum == ders.bolum:
        puan += 10
    elif hasattr(derslik, "blok") and hasattr(derslik.blok, "blok_onceligi"):
        puan += max(0, 6 - derslik.blok.blok_onceligi)

    # Dersin öncelik numarası yüksekse ekstra puan
    puan += ders.oncelik_numarasi

    return puan

def kısıt_var_mi(ders, derslik, zaman, atamalar, tum_dersler):
    # 1. Kapasite mutlak üst sınırı
    if ders.ogrenci_sayisi > derslik.kapasite + HATA_PAYI:
        return False, "Derslik kapasitesi yetersiz."

    # 2. Engelli erişim zorunluluğu
    if ders.engelli_erişim_gerektiriyor and not derslik.erisilebilirlik:
        return False, "Engelli erişimine uygun derslik yok."

    # 3. Laboratuvar gerekliliği
    if ders.ders_turu in ["uygulama", "laboratuvar"] and not derslik.laboratuvar_uygunlugu:
        return False, "Laboratuvar/uygulamalı ders için uygun derslik yok."

    # 4. Çakışmalar
    for d_id, (z, dslk) in atamalar.items():
        other = tum_dersler.get(ders_id=d_id)
        if z.gun == zaman.gun:
            other_bas = z.saat
            other_bitis = bitis_saati_hesapla(z.saat, other.ders_uzunlugu)
            bu_bas = zaman.saat
            bu_bitis = bitis_saati_hesapla(zaman.saat, ders.ders_uzunlugu)
            if zaman_araliklari_cakisiyor(z.gun, other_bas, other_bitis, zaman.gun, bu_bas, bu_bitis):
                if dslk.derslik_id == derslik.derslik_id:
                    return False, "Bu saat ve derslikte başka ders var (aralık çakışıyor)."
                if other.ogretmen.kullanici_id == ders.ogretmen.kullanici_id:
                    return False, "Öğretim üyesi bu zaman aralığında başka derste."
                if other.sinif == ders.sinif:
                    return False, "Aynı sınıf (dönem) için bu zaman aralığında iki ders olamaz."



    # 5. Öğretim üyesi özel durumları
    ozel_durumlar = OzelDurum.objects.filter(kullanici=ders.ogretmen)
    for durum in ozel_durumlar:
        if durum.gun == zaman.gun and durum.saat == zaman.saat:
            return False, f"Öğretim üyesinin özel durumu var: {durum.aciklama}"

    return True, ""

def ders_programi_olustur():
    dersler = Ders.objects.all().order_by('-oncelik_numarasi')
    derslikler = Derslik.objects.all()
    zamanlar = Zaman.objects.all()

    atamalar = {}
    kalan_dersler = []

    for ders in dersler:
        uygunlar = []
        neden_ekle = []
        for zaman in zamanlar:
            for derslik in derslikler:
                kısıt_ok, neden = kısıt_var_mi(ders, derslik, zaman, atamalar, Ders.objects)
                if kısıt_ok:
                    puan = atama_puani(ders, derslik, zaman)
                    if puan > -100:
                        uygunlar.append((puan, zaman, derslik))
                else:
                    neden_ekle.append(neden)
        # Uygun atamalar arasında en yüksek puanlı olanı seç
        if uygunlar:
            uygunlar.sort(reverse=True, key=lambda x: x[0])
            puan, zaman, derslik = uygunlar[0]
            atamalar[ders.ders_id] = (zaman, derslik)
            DersProgrami.objects.create(
                ders=ders,
                derslik=derslik,
                bolum=ders.bolum,
                sorumlu=ders.ogretmen,
                time=zaman.saat,
                date=zaman.gun
            )
        else:
            kalan_dersler.append((ders, set(neden_ekle)))  # Nedenler tekrar edebilir, set ile özetlenir

    if kalan_dersler:
        print("Atanamayan dersler:")
        for ders, nedenler in kalan_dersler:
            print(f"- {ders.ders_adi} ({ders.ders_id}): {'; '.join(list(nedenler))}")

    return atamalar, kalan_dersler


def bitis_saati_hesapla(baslangic, uzunluk):
    baslangic = baslangic.replace('.', ':')
    dt = datetime.strptime(baslangic, "%H:%M")
    dt_bitis = dt + timedelta(hours=uzunluk)
    return dt_bitis.strftime("%H:%M")

def ders_programi_olustur_siniflara_gore():
    """
    Her sınıf (1. sınıf, 2. sınıf, ...) için ayrı program ve kalan dersler listesi üretir.
    Geriye bir dict döner:
      {
        1: { 'atamalar': {...}, 'kalan_dersler': [...] },
        2: { ... }
      }
    """
    # Burada 'sinif' veya 'sinif' alanını kullanıyoruz, kendi modeline göre uyarlayabilirsin.
    tum_siniflar = Ders.objects.values_list('sinif', flat=True).distinct()  # veya 'sinif'
    tum_siniflar = sorted(set(tum_siniflar))

    sinif_programlari = {}

    for sinif_no in tum_siniflar:
        dersler = Ders.objects.filter(sinif=sinif_no).order_by('-oncelik_numarasi')
        derslikler = Derslik.objects.all()
        zamanlar = Zaman.objects.all()

        atamalar = {}
        kalan_dersler = []

        for ders in dersler:
            uygunlar = []
            neden_ekle = []
            for zaman in zamanlar:
                for derslik in derslikler:
                    kısıt_ok, neden = kısıt_var_mi(ders, derslik, zaman, atamalar, Ders.objects)
                    if kısıt_ok:
                        puan = atama_puani(ders, derslik, zaman)
                        if puan > -100:
                            uygunlar.append((puan, zaman, derslik))
                    else:
                        neden_ekle.append(neden)
            if uygunlar:
                uygunlar.sort(reverse=True, key=lambda x: x[0])
                puan, zaman, derslik = uygunlar[0]
                atamalar[ders.ders_id] = (zaman, derslik)
                DersProgrami.objects.create(
                    ders=ders,
                    derslik=derslik,
                    bolum=ders.bolum,
                    sorumlu=ders.ogretmen,
                    time=zaman.saat,
                    date=zaman.gun
                )
            else:
                print(f"OLAMADI: {ders.ders_adi} — {neden_ekle}")
                kalan_dersler.append((ders, set(neden_ekle)))

        sinif_programlari[sinif_no] = {
            'atamalar': atamalar,
            'kalan_dersler': kalan_dersler
        }

    return sinif_programlari


def zaman_araliklari_cakisiyor(gun1, bas1, bitis1, gun2, bas2, bitis2):
    if gun1 != gun2:
        return False
    bas1_dt = datetime.strptime(bas1, "%H:%M")
    bitis1_dt = datetime.strptime(bitis1, "%H:%M")
    bas2_dt = datetime.strptime(bas2, "%H:%M")
    bitis2_dt = datetime.strptime(bitis2, "%H:%M")
    return bas1_dt < bitis2_dt and bas2_dt < bitis1_dt
