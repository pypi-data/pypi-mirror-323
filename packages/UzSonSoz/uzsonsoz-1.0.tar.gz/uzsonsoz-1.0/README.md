# UzSonSoz

UzSonSoz — bu o‘zbek tilidagi sonlarni so‘z bilan ifodalash va aksincha so‘zlarni songa aylantirish uchun yaratilgan kutubxona. Ushbu kutubxona sonlarni o'qish va yozish uchun qulay va samarali hisoblanadi.

**Muallif: [Dasturbek](https://github.com/ddasturbek)**

## Xususiyatlar

* O‘zbek tilidagi sonlarni aniq va to‘g‘ri so‘z bilan ifodalaydi.
* 0 dan 999 999 999 999 gacha bo‘lgan sonlar ustida ishlaydi.
* O‘rnatish va ishlatish juda oson.

## O'rnatish

Siz dasturni Python loyihangizga [pip](https://pypi.org/project/UzSonSoz) orqali o‘rnatib foydalanishingiz mumkin.

```bash
pip install UzSonSoz
```

Kompyuterga o‘rnatish uchun quyidagi buyruqni terminalga kiritishingiz mumkin:

```bash
git clone https://github.com/ddasturbek/UzSonSoz.git
```

## Foydalanish

Kutubxona yordamida **sonlarni so‘z** bilan ifodalash uchun quyidagi sintaksisni ishlatishingiz mumkin:

```bash
import UzSonSoz as USS

print(USS.SondanSozga(0))  # nol
print(USS.SondanSozga(1))  # bir
print(USS.SondanSozga(22))  # yigirma ikki
print(USS.SondanSozga(335))  # uch yuz o‘ttiz besh
print(USS.SondanSozga(7996))  # yetti ming to‘qqiz yuz to‘qson olti
print(USS.SondanSozga(681674))  # olti yuz sakson bir ming olti yuz yetmish to‘rt
print(USS.SondanSozga(645842780))  # olti yuz qirq besh million sakkiz yuz qirq ikki ming yetti yuz sakson
```

Kutubxona yordamida **so‘zlarni son** bilan ifodalash uchun quyidagi sintaksisni ishlatishingiz mumkin:

```bash
import UzSonSoz as USS

print(USS.SozdanSonga('NOL'))  # 0
print(USS.SozdanSonga('Bir'))  # 1
print(USS.SozdanSonga('o\'ttiz olti'))  # 36
print(USS.SozdanSonga('to‘rt yuz sakson sakkiz'))  # 488
print(USS.SozdanSonga('Uch Ming Olti Yuz Qirq Yetti'))  # 3647
print(USS.SozdanSonga('yettiz yuz ellik olti ming ellik'))  # 756050
print(USS.SozdanSonga('O‘ttiz to‘qqiz MILLION yetti yuz to‘qson olti MING bir YUZ ellik bir'))  # 39796151

print(USS.SozdanSonga('Boshqa so‘z'))  # Boshqa so‘z
```

*So‘zlarni songa aylantirganda, funksiya so‘zlarning katta-kichikligini inobatga olmagan holda to‘g‘ri ishlaydi!*
