# Minik Bulut'un Renk Avı ☁️

30 saniyelik, dikey (720×1280) çocuklara uygun YouTube Shorts animasyonu. Kırmızı elma, sarı güneş ve mavi balığı tanıtır; Türkçe altyazılar ve tamamen kodla üretilen hafif bir melodi içerir.

## Gereksinimler

- Python 3.9+
- Pillow: `python -m pip install Pillow`
- FFmpeg (komut satırında `ffmpeg` olarak erişilebilir olmalı)

## Oluşturma

```bash
python -m pip install Pillow
python create_short.py
```

Videonun adı `minik-bulut-renk-avi.mp4` olur. Farklı bir yol belirtmek için:

```bash
python create_short.py --output output/renk-avi.mp4
```

Video 30 saniye, 30 FPS, H.264/AAC ve 9:16 oranındadır. Seslendirme yerine çocukların ekrandan okuyabileceği Türkçe metinler ve orijinal, sentetik arka plan melodisi kullanır.
