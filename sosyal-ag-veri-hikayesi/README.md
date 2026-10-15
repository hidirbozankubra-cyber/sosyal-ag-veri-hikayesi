# Türkiye'de sosyal ağ kullanımı, 2014–2025 · Veri hikâyesi

Eurostat verisiyle hazırlanmış scrollytelling (kaydırarak anlatım) sitesi. Kullanıcı Arayüz Tasarımı dersi projesi.

**Canlı site:** [BAĞLANTI] · **Portfolyo:** https://kubrahidirbozan-ruby.vercel.app/ · **LinkedIn gönderisi:** [BAĞLANTI]

## Çalışma sorusu
Türkiye'de sosyal ağ kullanımı 2014–2025 arasında AB ortalamasına ve diğer Avrupa ülkelerine göre nasıl değişti?

## Ana bulgular
Sayılar `data/processed/facts.json` dosyasındadır (notebook üretir):
1. Türkiye %38,2'den %80,4'e çıktı ve 2017'de AB ortalamasını kalıcı olarak geçti.
2. 2025'te 36 ülke arasında 9. sırada; AB-27 ortalamasının yaklaşık 13 puan üstünde.
3. 2014'te düşük başlayan ülkeler daha çok artırdı (r ≈ −0,55; ilişki, nedensellik değil).

## Depo yapısı
```
├── README.md
├── data/
│   ├── raw/            Eurostat tin00127 ham dosyası (erişim: 12.10.2026)
│   └── processed/      tidy.csv, summary.json, facts.json (notebook çıktısı)
├── notebooks/analiz.ipynb   temizleme, EDA, bulgular, dışa aktarım (çalıştırılmış hâliyle)
├── site/                    index.html, css/, js/, data/ (processed'in kopyası), og.png
├── docs/                    storyboard.pdf, tasarim-kararlari.pdf, linkedin-metni.txt,
│                            paylasim-gorseli.png, lighthouse/, ekran-goruntuleri/
└── tools/                   notebook ve docs dosyalarını üreten betikler
```

## Yeniden üretme
```bash
pip install pandas numpy openpyxl matplotlib jupyter
cd notebooks && jupyter nbconvert --to notebook --execute --inplace analiz.ipynb   # data/processed + site/data üretir
cd ../site && python -m http.server 8000        # http://localhost:8000
```

## Yayına alma
**GitHub Pages:** depoyu herkese açık yapıp `main`'e yükleyin → Settings → Pages → Source: **GitHub Actions**. `.github/workflows/pages.yml` yalnızca `site/` klasörünü yayınlar. Adres: `https://hidirbozankubra-cyber.github.io/sosyal-ag-veri-hikayesi/`.
**Netlify / Vercel:** depoyu bağlayın, *Publish directory* = `site`, build komutu boş.

## Teknik tercihler ve kaynaklar
- Analiz: Python (pandas, numpy, Jupyter).
- Kaydırma tetikleme: tarayıcıların **Intersection Observer API**'si (saf JavaScript). Dış kütüphane kodu kullanılmadı.
- Grafikler: elle yazılmış SVG (D3 kullanılmadı); tüm değerler `site/data/*.json` dosyalarından okunur, kodda elle sayı yoktur.
- Yazı tipi: sistem yazı tipleri (Georgia + system-ui). Harici bağımlılık yok.
- Veri: Eurostat, *tin00127*; yeniden kullanım: CC BY 4.0.

## Yapay zekâ kullanım beyanı
Analiz kodu ve site, Claude (Anthropic) ile birlikte hazırlandı; veri, bulgular ve metinler yazar tarafından kontrol edildi. [Kendi katkınıza göre düzenleyin.]

## Doldurulacak yer tutucular
Yayına aldıktan sonra yalnızca README'deki `[BAĞLANTI]` alanları, `docs/linkedin-metni.txt` içindeki bağlantılar ve `docs/paylasim-gorseli.png` altındaki adres kalır. `site/index.html` içindeki GitHub depo adresi `hidirbozankubra-cyber/sosyal-ag-veri-hikayesi` olarak yazıldı; depo adınız farklıysa değiştirin.

## Lighthouse (mobil, yerel sunucu)
Performans 99 · Erişilebilirlik 100 · En İyi Uygulamalar 100 · SEO 100. Rapor: `docs/lighthouse/`. Canlı adres yayına girince testi yeniden çalıştırıp ekran görüntülerini güncelleyin.
