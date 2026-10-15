import nbformat as nbf
nb=nbf.v4.new_notebook(); C=[]
md=lambda s:C.append(nbf.v4.new_markdown_cell(s.strip())); code=lambda s:C.append(nbf.v4.new_code_cell(s.strip()))
md("""# Avrupa'da sosyal ağ kullanımı, 2014–2025: Türkiye nerede?
**Çalışma sorusu:** Türkiye'de sosyal ağ kullanımı 2014–2025 arasında AB ortalamasına ve diğer Avrupa ülkelerine göre nasıl değişti?

**Veri:** Eurostat, *Individuals using the internet for participating in social networks* (`tin00127`). 16–74 yaş bireylerin son 3 ayda özel amaçla sosyal ağ kullanım oranı (%). Kaynak: Eurostat yıllık BİT hane halkı anketi. Erişim: 12.10.2026.

**Akış:** veri yükleme → temizleme → keşifsel analiz → bulgular → site için özet dosyaların üretimi.""")
code("""import json, shutil
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
RAW = Path("../data/raw/tin00127_page_spreadsheet.xlsx")
OUT = Path("../data/processed"); OUT.mkdir(parents=True, exist_ok=True)
SITE = Path("../site/data"); SITE.mkdir(parents=True, exist_ok=True)
ACC, INK, GRY = "#D55E00", "#1b1b1f", "#7a7a82"   # sitedeki palet ile aynı""")
md("## 1. Veri yükleme\nEurostat dosyası `Sheet 1` sayfasında **geniş** biçimde: her yılın yanında bir *bayrak* sütunu var (ör. `b` = seri kesintisi). Üst bilgi satırlarını ve ülke bloğunun yerini sabit numara yerine başlık metninden buluyoruz.")
code("""raw = pd.read_excel(RAW, sheet_name="Sheet 1", header=None)
print(raw.iloc[0,0]); print(raw.iloc[1,0], raw.iloc[1,1]); print(raw.iloc[2,0], raw.iloc[2,1])
hdr = raw.index[raw[0] == "TIME"][0]
years = [int(y) for y in raw.iloc[hdr, 1:].dropna()]
start = raw.index[raw[0] == "GEO (Labels)"][0] + 1
end = raw.iloc[start:].index[raw.iloc[start:, 0].isna().values][0]
block = raw.iloc[start:end]
print("Yıllar:", years[0], "-", years[-1], "| ülke/bölge satırı:", len(block))""")
md("## 2. Temizleme\nHer gözlem için **değer** ve **bayrak** sütunlarını ayırıp *uzun (tidy)* tabloya çeviriyoruz. `:` Eurostat'ta \"veri yok\" demektir; sayıya çevrilemediği için eksik (`NaN`) olur. Tahmin ya da doldurma yapmıyoruz.")
code("""recs = []
for _, r in block.iterrows():
    for i, y in enumerate(years):
        v = pd.to_numeric(r[1 + 2*i], errors="coerce")
        f = r[2 + 2*i]
        recs.append((r[0], y, v, f.strip() if isinstance(f, str) else ""))
df = pd.DataFrame(recs, columns=["geo", "year", "value", "flag"])
print("Toplam hücre:", len(df), "| eksik:", df.value.isna().sum(), f"(%{df.value.isna().mean()*100:.1f})")""")
md("""### Temizleme kararları ve gerekçeleri
1. **Euro bölgesi serileri çıkarıldı.** Üç ayrı euro bölgesi satırı (19/20/21 ülke) var, ancak hepsi tamamen eksik. Doldurulacak veri yok.
2. **Liechtenstein çıkarıldı.** Hiçbir yılda verisi yok.
3. **AB-27 ortalaması ayrı seri olarak tutuldu.** Ülke sıralamalarına karıştırılmayacak, referans çizgisi olacak.
4. **Kısmi verisi olan ülkeler (İzlanda, İsviçre, Birleşik Krallık, Kosova vb.) tutuldu**, ama karşılaştırmalar yalnızca ilgili iki yılın verisi olan ülkelerle yapılacak. Böylece sıralama, yıllar arasında farklı ülke kümelerini karıştırmaz.
5. **Aykırı değer silinmedi.** Anket verisinde büyük sıçramalar gerçek olabilir; aşağıda kontrol ediyoruz ve kesinti (`b`) bayraklarıyla birlikte not ediyoruz.""")
code("""euro = df[df.geo.str.startswith("Euro area")]
assert euro.value.isna().all(), "Euro bölgesi satırlarında veri var, karar gözden geçirilmeli"
tidy = df[~df.geo.str.startswith("Euro area")].copy()
tidy["geo"] = tidy.geo.replace({"European Union - 27 countries (from 2020)": "EU27"})
allmiss = tidy.groupby("geo").value.apply(lambda s: s.isna().all())
print("Tamamen eksik olanlar:", list(allmiss[allmiss].index))
tidy = tidy[~tidy.geo.isin(allmiss[allmiss].index)]
print("Kalan ülke/seri sayısı:", tidy.geo.nunique())
tidy.groupby("geo").value.count().sort_values().head(8)""")
code("""w = tidy.pivot(index="geo", columns="year", values="value")
d = w.diff(axis=1).stack()
print(d[d.abs() > 12].round(1).rename("değişim (puan)").to_string())
print("\\nKesinti (b) bayraklı gözlem sayısı:", (tidy.flag == "b").sum())
print(tidy[tidy.flag == "b"].groupby("geo").year.apply(list).to_string())""")
md("**Karar:** 12 puandan büyük yıllık değişim 5 gözlemde var. Yalnızca Belçika 2021 düşüşü kesinti (`b`) bayraklı; Belçika ve Almanya 2015, Kosova ve Slovenya 2020 sıçramaları bayraksız. Bunların hatalı olduğunu kanıtlayacak bir dayanak yok, bu yüzden **silmedik**; fakat bu ülkeler ana hikâyede kullanılmıyor ve sitede kesinti yılları (`breaks`) okuyucuya gösteriliyor. Türkiye'nin 2022'deki 10,8 puanlık sıçraması eşiğin altında ve bayraksız; nedeni bu veriyle açıklanamaz, sitede de öyle söylüyoruz.")
code("""tidy = tidy.dropna(subset=["value"]).reset_index(drop=True)
print(len(tidy), "gözlem,", tidy.geo.nunique(), "ülke/seri,", tidy.year.min(), "-", tidy.year.max())""")
md("## 3. Keşifsel analiz\n### 3.1 AB-27 ortalaması ve Türkiye zaman içinde")
code("""w = tidy.pivot(index="geo", columns="year", values="value")
cmp = w.loc[["EU27", "Türkiye"]].T.round(1); cmp["fark"] = (cmp["Türkiye"] - cmp["EU27"]).round(1)
cmp""")
code("""fig, ax = plt.subplots(figsize=(7, 3.6))
ax.plot(w.columns, w.loc["EU27"], "--", color=INK, label="AB-27")
ax.plot(w.columns, w.loc["Türkiye"], color=ACC, lw=3, label="Türkiye")
ax.set(ylabel="% (16–74 yaş)", title="Türkiye 2017'de AB ortalamasını geçti"); ax.legend(); plt.show()""")
md("### 3.2 2025 sıralaması\nSıralama yalnızca o yıl verisi olan ülkeleri kapsar (kaç ülke olduğu yıla göre değişir).")
code("""r25 = w[2025].drop("EU27").dropna().sort_values(ascending=False)
print(len(r25), "ülke"); r25.round(1).head(10).to_frame("2025 (%)")""")
md("### 3.3 Geriden başlayan daha çok arttı mı?\nHer iki yılda da verisi olan ülkeler için 2014 düzeyi ile 2014→2025 değişimi (puan = iki yüzde arasındaki fark) karşılaştırılır. **Korelasyon** (r), iki değişkenin birlikte hareket etme derecesidir (−1…+1); nedensellik göstermez.")
code("""both = w[[2014, 2025]].dropna().drop("EU27")
both["degisim"] = both[2025] - both[2014]
r = np.corrcoef(both[2014], both["degisim"])[0, 1]
print(len(both), "ülke | r =", round(r, 2))
fig, ax = plt.subplots(figsize=(6, 3.8)); ax.scatter(both[2014], both.degisim, c=GRY)
ax.scatter(both.loc["Türkiye", 2014], both.loc["Türkiye", "degisim"], c=ACC, s=80, marker="^")
ax.set(xlabel="2014 (%)", ylabel="Değişim (puan)", title="Başlangıcı düşük olan daha çok artırdı"); plt.show()""")
md("### 3.4 Ülkeler birbirine yaklaştı mı?\nStandart sapma, ülkelerin ortalamadan ne kadar saçıldığını gösterir.")
code("""sd14, sd25 = both[2014].std(), both[2025].std(); print(round(sd14, 1), "→", round(sd25, 1))""")
md("## 4. Bulgular ve doğrulama\nSitede kullanılacak tüm sayıları burada hesaplıyoruz; site bunları `facts.json` dosyasından okur, metne elle sayı yazılmaz. Hikâyedeki sözel iddialar (\"ikiye katlandı\", \"AB'yi geçti\") `assert` ile doğrulanır.")
code("""g = lambda c, y: float(w.loc[c, y])
eu, tr = w.loc["EU27"], w.loc["Türkiye"]
above = (tr > eu)
cross = int(next(y for y in years if above.loc[y:].all()))
rank25 = int(r25.rank(ascending=False)["Türkiye"])
F = dict(
  y0=years[0], y1=years[-1], eu14=round(g("EU27",2014),1), eu25=round(g("EU27",2025),1),
  tr14=round(g("Türkiye",2014),1), tr25=round(g("Türkiye",2025),1),
  eu_delta=round(g("EU27",2025)-g("EU27",2014),1), tr_delta=round(g("Türkiye",2025)-g("Türkiye",2014),1),
  tr_ratio=round(g("Türkiye",2025)/g("Türkiye",2014),1),
  gap14=int(round(g("EU27",2014)-g("Türkiye",2014))), gap25=int(round(g("Türkiye",2025)-g("EU27",2025))),
  cross_year=cross, cross_i=cross-years[0], cross_tr=round(g("Türkiye",cross),1), cross_eu=round(g("EU27",cross),1),
  tr20=round(g("Türkiye",2020),1), tr21=round(g("Türkiye",2021),1), tr22=round(g("Türkiye",2022),1),
  i20=2020-years[0], i21=2021-years[0], i22=2022-years[0],
  jump=round(g("Türkiye",2022)-g("Türkiye",2021),1),
  dk25=round(g("Denmark",2025),1), it25=round(g("Italy",2025),1),
  rank25=rank25, n25=int(len(r25)), r=round(float(r),2), n_both=int(len(both)),
  sd14=round(float(sd14),1), sd25=round(float(sd25),1),
  n_obs=int(len(tidy)), n_cells=int(len(df)), n_missing=int(df.value.isna().sum()), n_geo=int(tidy.geo.nunique()-1))
assert F["tr_ratio"] >= 2.0, "ikiye katlandı iddiası tutmuyor"
assert 75 <= F["tr25"] <= 85, "her 5 kişiden 4'ü iddiası tutmuyor"
assert F["tr14"] < F["eu14"] and F["tr25"] > F["eu25"], "AB'yi geçti iddiası"
assert F["tr21"] < F["tr20"] < F["tr22"], "2021 düşüş / 2022 sıçrama"
assert F["r"] < -0.3, "geriden başlayan daha çok arttı iddiası"
F""")
md("## 5. Site için özet dosyaların üretimi\nSite ham veriyi değil, yalnızca bu küçük özet dosyaları kullanır (5 MB sınırının çok altında).")
code("""TR = {"EU27":"AB-27 ortalaması","Belgium":"Belçika","Bulgaria":"Bulgaristan","Czechia":"Çekya","Denmark":"Danimarka","Germany":"Almanya","Estonia":"Estonya","Ireland":"İrlanda","Greece":"Yunanistan","Spain":"İspanya","France":"Fransa","Croatia":"Hırvatistan","Italy":"İtalya","Cyprus":"Kıbrıs","Latvia":"Letonya","Lithuania":"Litvanya","Luxembourg":"Lüksemburg","Hungary":"Macaristan","Malta":"Malta","Netherlands":"Hollanda","Austria":"Avusturya","Poland":"Polonya","Portugal":"Portekiz","Romania":"Romanya","Slovenia":"Slovenya","Slovakia":"Slovakya","Finland":"Finlandiya","Sweden":"İsveç","Iceland":"İzlanda","Norway":"Norveç","Switzerland":"İsviçre","United Kingdom":"Birleşik Krallık","Montenegro":"Karadağ","North Macedonia":"Kuzey Makedonya","Albania":"Arnavutluk","Serbia":"Sırbistan","Türkiye":"Türkiye","Bosnia and Herzegovina":"Bosna-Hersek","Kosovo*":"Kosova*"}
missing = set(tidy.geo) - set(TR); assert not missing, missing
summary = {
  "years": years,
  "series": {TR[c]: [None if pd.isna(x) else round(float(x),1) for x in w.loc[c].reindex(years)] for c in w.index},
  "scatter": [{"c": TR[c], "x": round(float(both.loc[c,2014]),1), "y": round(float(both.loc[c,"degisim"]),1)} for c in both.index],
  "breaks": {TR[c]: sorted(map(int, g_.year)) for c, g_ in tidy[tidy.flag=="b"].groupby("geo")}}
tidy.assign(geo_tr=tidy.geo.map(TR)).to_csv(OUT/"tidy.csv", index=False)
(OUT/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, separators=(",",":")), encoding="utf-8")
(OUT/"facts.json").write_text(json.dumps(F, ensure_ascii=False, indent=1), encoding="utf-8")
for f in ["summary.json", "facts.json"]: shutil.copy(OUT/f, SITE/f)
print({f.name: f.stat().st_size for f in OUT.iterdir()})""")
nb.cells=C; nb.metadata={"kernelspec":{"name":"python3","display_name":"Python 3","language":"python"}}
nbf.write(nb,"notebooks/analiz.ipynb")
