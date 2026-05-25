# filigran

Görsellere filigran eklemek için masaüstü uygulaması. Görsel veya yazı filigranı ekle, saydamlığını ayarla, sürükle-bırak ile konumlandır.

## Özellikler

- Ana görsel: PNG, JPG, WEBP, BMP, TIFF, GIF
- Filigran görseli: yarı saydam, sürükle-bırak ile konumlandırılabilir
- Yazı filigranı: boyut ve saydamlık ayarı
- Çıktıyı PNG, JPG veya WebP olarak kaydet

## Kurulum ve çalıştırma

Python 3.8+ gereklidir.

```bash
pip install -r requirements.txt
python filigran.py
```

## .exe olarak derleme (Windows)

`build.bat` dosyasına çift tıkla. `dist/filigran.exe` oluşur.

Ya da terminalden:

```bash
pip install -r requirements.txt
pyinstaller --onefile --windowed --name filigran filigran.py
```

## Lisans

MIT
