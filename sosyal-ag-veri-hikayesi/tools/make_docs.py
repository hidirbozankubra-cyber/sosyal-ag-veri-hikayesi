"""docs/ altındaki teslim dosyalarını üretir: storyboard.pdf, tasarim-kararlari.pdf, paylasim-gorseli.png, linkedin-metni.txt"""
import json, textwrap
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
ROOT = Path(__file__).resolve().parent.parent
D = json.load(open(ROOT/"data/processed/summary.json")); F = json.load(open(ROOT/"data/processed/facts.json"))
n = lambda v, dp=1: f"{v:.{dp}f}".replace(".", ",").replace("-", "−")
ACC, INK, MUT, GRY, BG, ACCT, CARD, LINE = "#EBA8BB", "#f5ecef", "#c2b2ba", "#8f808a", "#151015", "#F2BDCB", "#211920", "#3b2f38"
plt.rcParams.update({"text.color": INK, "axes.edgecolor": GRY, "axes.labelcolor": MUT, "xtick.color": MUT, "ytick.color": MUT, "figure.facecolor": BG, "axes.facecolor": CARD, "savefig.facecolor": BG})
Y = D["years"]; S = D["series"]; EU, TR = S["AB-27 ortalaması"], S["Türkiye"]

# ---------------- STORYBOARD ----------------
def line(ax, series, upto=None, note=None, nx=None, ny=None):
    up = len(Y)-1 if upto is None else upto
    for v, c, ls, lw, lbl in series:
        xs = [y for i, y in enumerate(Y) if i <= up and v[i] is not None]; ys = [x for i, x in enumerate(v) if i <= up and x is not None]
        ax.plot(xs, ys, color=c, ls=ls, lw=lw); ax.text(xs[-1]+.2, ys[-1], lbl, color=c, fontsize=7, va="center")
    ax.set_xlim(2013.5, 2027); ax.set_ylim(30, 100)
    if note: ax.annotate(note, xy=(nx, ny), xytext=(nx-3.5 if nx > 2018 else nx+0.5, ny+14), fontsize=7, fontweight="bold", arrowprops=dict(arrowstyle="-", color=INK))
def bars(ax):
    rows = sorted([(c, v[-1]) for c, v in S.items() if c != "AB-27 ortalaması" and v[-1] is not None], key=lambda r: -r[1])[:14]
    ax.barh(range(len(rows)), [r[1] for r in rows], color=[ACC if r[0] == "Türkiye" else GRY for r in rows]); ax.invert_yaxis()
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=6); ax.axvline(F["eu25"], color=MUT, ls="--"); ax.set_xlim(0, 100)
    ax.text(F["eu25"], -1, f"AB-27 %{n(F['eu25'])}", fontsize=7, ha="center", fontweight="bold")
def scat(ax):
    for p in D["scatter"]: ax.scatter(p["x"], p["y"], c=ACC if p["c"] == "Türkiye" else GRY, marker="^" if p["c"] == "Türkiye" else "o", s=22)
    ax.set_xlabel("2014 (%)", fontsize=7); ax.set_ylabel("değişim (puan)", fontsize=7); ax.text(60, 40, f"r = {n(F['r'],2)}", fontsize=8, fontweight="bold")
def sel(ax):
    line(ax, [(EU, MUT, "--", 1.5, "AB-27"), (TR, ACC, "-", 2.5, "Türkiye"), (S["Almanya"], INK, "-", 1.5, "seçilen")])
    ax.text(2014, 92, "[Ülke ▼]  [İkinci ülke ▼]", fontsize=8, bbox=dict(boxstyle="round", fc=CARD, ec=INK))
eu1, tr1 = (EU, MUT, "--", 1.8, "AB-27"), (TR, ACC, "-", 2.8, "Türkiye")
frames = [
 ("Açılış (Hero)", f"Başlık: Türkiye'de sosyal ağ kullanımı 11 yılda ikiye katlandı: 2025'te her 5 kişiden 4'ü ağda. Alt başlık, yazar, tarih, %{n(F['tr14'])} → %{n(F['tr25'])} büyük sayılar, 'Aşağı kaydırın'.", None),
 ("Bulgu 1 · Adım 1", f"AB'de 2014'te her 10 kişiden yaklaşık 4'ü sosyal ağdaydı (%{n(F['eu14'])}).", lambda a: line(a, [eu1], 0, f"2014: %{n(F['eu14'])}", 2014, F['eu14'])),
 ("Bulgu 1 · Adım 2", f"AB ortalaması 11 yılda {n(F['eu_delta'])} puan arttı: %{n(F['eu25'])}.", lambda a: line(a, [eu1], None, f"2025: %{n(F['eu25'])}", 2025, F['eu25'])),
 ("Bulgu 1 · Adım 3", f"Türkiye çizgisi eklenir: 2014'te %{n(F['tr14'])}, AB'nin ~{F['gap14']} puan altı.", lambda a: line(a, [eu1, tr1], 0, f"Türkiye %{n(F['tr14'])}", 2014, F['tr14'])),
 ("Bulgu 1 · Adım 4", f"{F['cross_year']}'de Türkiye AB ortalamasını geçti ve bir daha altına inmedi.", lambda a: line(a, [eu1, tr1], F['cross_i'], f"{F['cross_year']}: geçiş", F['cross_year'], F['cross_tr'])),
 ("Bulgu 1 · Adım 5", f"2021'de artış durdu: %{n(F['tr20'])} → %{n(F['tr21'])}. Nedeni bu veriyle söylenemez.", lambda a: line(a, [eu1, tr1], F['i21'], f"2021: %{n(F['tr21'])}", 2021, F['tr21'])),
 ("Bulgu 1 · Adım 6", f"2022'de tek yılda {n(F['jump'])} puanlık sıçrama: %{n(F['tr22'])}.", lambda a: line(a, [eu1, tr1], F['i22'], f"+{n(F['jump'])} puan", 2022, F['tr22'])),
 ("Bulgu 1 · Adım 7", f"2025: Türkiye %{n(F['tr25'])}, AB'nin ~{F['gap25']} puan üstünde. Danimarka ve İtalya bağlam olarak eklenir.", lambda a: line(a, [eu1, tr1, (S['Danimarka'], GRY, "-", 1.5, "Danimarka"), (S['İtalya'], GRY, "-", 1.5, "İtalya")], None, f"%{n(F['tr25'])}", 2025, F['tr25'])),
 ("Bulgu 2 · Sıralama + yıl kaydırıcısı", f"2025'te Türkiye {F['n25']} ülke arasında {F['rank25']}. sırada. Kaydırıcı yılı değiştirir; telefonda ilk 10 + Türkiye + son 2 gösterilir.", bars),
 ("Bulgu 3 · Saçılım", f"Geriden başlayanlar daha çok artırdı (r = {n(F['r'],2)}): ilişki var, nedensellik iddiası yok. Türkiye ve en çok/en az artanlar etiketli.", scat),
 ("Okuyucu keşfi", "İki açılır kutu: ülke ve ikinci ülke. Çizgi grafik Türkiye ve AB ile birlikte güncellenir; başlık değişimi özetler.", sel),
 ("Sonuç · Yöntem · Yazar", "Peki ne olmuş? çıkarımlar, sınırlılıklar, açık sorular. Yöntem: kaynak, temizleme, araçlar, YZ beyanı. Yazar ve bağlantılar, portfolyoya dönüş.", None)]
with PdfPages(ROOT/"docs/storyboard.pdf") as pdf:
    for pg in range(2):
        fig = plt.figure(figsize=(11.69, 8.27), facecolor=BG)
        fig.text(.04, .965, f"Storyboard · Türkiye'de sosyal ağ kullanımı · sayfa {pg+1}/2", fontsize=11, fontweight="bold", va="top")
        fig.text(.04, .94, "Her kare: solda adımda okunan metin, sağda grafiğin o andaki hali (vurgulanan/eklenen öğe).", fontsize=8, color=MUT, va="top")
        for k in range(6):
            i = pg*6+k; title, txt, fn = frames[i]; r, c = divmod(k, 2)
            x0, y0 = .04+c*.48, .62-r*.31
            fig.patches.append(plt.Rectangle((x0, y0), .46, .29, transform=fig.transFigure, fill=False, ec=INK, lw=1))
            fig.text(x0+.01, y0+.275, f"{i+1}. {title}", fontsize=8.5, fontweight="bold", va="top")
            fig.text(x0+.01, y0+.245, "\n".join(textwrap.wrap(txt, 31)), fontsize=8, va="top", linespacing=1.4)
            if fn:
                ax = fig.add_axes([x0+.22, y0+.04, .225, .19], facecolor=CARD)
                fn(ax); ax.tick_params(labelsize=6); [s.set_color(GRY) for s in ax.spines.values()]
        pdf.savefig(fig); plt.close(fig)

# ---------------- PAYLAŞIM GÖRSELİ ----------------
from PIL import Image, ImageDraw, ImageFont
fp = "/usr/share/fonts/truetype/dejavu/"
fS, fB, fR = (lambda s: ImageFont.truetype(fp+"DejaVuSerif-Bold.ttf", s)), (lambda s: ImageFont.truetype(fp+"DejaVuSans-Bold.ttf", s)), (lambda s: ImageFont.truetype(fp+"DejaVuSans.ttf", s))
W, H = 1200, 627; im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
d.rectangle([0, 0, 14, H], fill=ACC)
d.text((60, 50), "VERİ HİKÂYESİ · EUROSTAT · 2014–2025", font=fB(20), fill=MUT)
for i, t in enumerate(["Türkiye'de sosyal ağ", "kullanımı 11 yılda", "ikiye katlandı"]): d.text((60, 100+i*66), t, font=fS(52), fill=ACC if i == 2 else INK)
d.text((60, 330), f"%{n(F['tr14'])}", font=fS(72), fill=MUT); d.text((318, 345), "→", font=fB(54), fill=MUT); d.text((400, 330), f"%{n(F['tr25'])}", font=fS(72), fill=ACC)
d.text((60, 420), "2014", font=fR(22), fill=MUT); d.text((400, 420), "2025", font=fR(22), fill=MUT)
d.text((60, 560), "Kübra Hıdırbozan · Büyük Veri Analistliği", font=fR(24), fill=INK)
x0, x1, y0, y1 = 700, 1140, 520, 120
pt = lambda v: [(x0+i*(x1-x0)/(len(Y)-1), y0-(val-30)/70*(y0-y1)) for i, val in enumerate(v)]
for g in range(30, 101, 10): d.line([(x0, y0-(g-30)/70*(y0-y1))]*1+[(x1, y0-(g-30)/70*(y0-y1))], fill=LINE, width=1)
pe = pt(EU); [d.line([pe[i], pe[i+1]], fill=MUT, width=4) for i in range(0, len(pe)-1, 2)]
d.line(pt(TR), fill=ACC, width=9, joint="curve")
d.text((x1-110, pt(TR)[-1][1]-40), "Türkiye", font=fB(24), fill=ACCT); d.text((x1-90, pt(EU)[-1][1]+12), "AB-27", font=fB(22), fill=MUT)
d.text((x0, y0+14), "2014", font=fR(18), fill=MUT); d.text((x1-45, y0+14), "2025", font=fR(18), fill=MUT)
im.save(ROOT/"docs/paylasim-gorseli.png"); im.save(ROOT/"site/og.png")

# ---------------- LINKEDIN METNİ ----------------
(ROOT/"docs/linkedin-metni.txt").write_text(f"""Türkiye'de sosyal ağ kullanımı 11 yılda ikiye katlandı: 2014'te %{n(F['tr14'])}, 2025'te %{n(F['tr25'])}.

Kullanıcı arayüz tasarımı dersi için Eurostat verisiyle etkileşimli bir veri hikâyesi yaptım. Avrupa'daki {F['n25']} ülkeyi karşılaştırdım:

• Türkiye {F['cross_year']}'de AB ortalamasını geçti ve bir daha altına inmedi
• 2022'de tek yılda {n(F['jump'])} puanlık sıçrama yaptı
• 2025'te {F['n25']} ülke arasında {F['rank25']}. sırada, AB ortalamasının yaklaşık {F['gap25']} puan üstünde

Sayfada kaydırdıkça grafik değişiyor; sonunda kendi ülkenizi seçip Türkiye ile karşılaştırabilirsiniz.

🔗 [site bağlantısı]
💻 Analiz notebook'u ve kod: [GitHub bağlantısı]

Araçlar: Python (pandas), HTML/CSS/JavaScript, SVG. Veri: Eurostat tin00127.

#veriGörselleştirme #veriHikâyeciliği #kullanıcıArayüzü #python #eurostat
""", encoding="utf-8")

# ---------------- TASARIM KARARLARI (1 sayfa PDF) ----------------
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
for nm, f in [("DV", "DejaVuSans.ttf"), ("DVB", "DejaVuSans-Bold.ttf"), ("DVS", "DejaVuSerif-Bold.ttf")]: pdfmetrics.registerFont(TTFont(nm, fp+f))
def lum(h):
    c = [int(h[i:i+2], 16)/255 for i in (1, 3, 5)]; c = [x/12.92 if x <= .03928 else ((x+.055)/1.055)**2.4 for x in c]; return .2126*c[0]+.7152*c[1]+.0722*c[2]
cr = lambda a, b: (max(lum(a), lum(b))+.05)/(min(lum(a), lum(b))+.05)
P = lambda t, s="b": Paragraph(t, ParagraphStyle(s, fontName="DV", fontSize=8, leading=10.5))
H2 = ParagraphStyle("h", fontName="DVS", fontSize=11, spaceBefore=6, spaceAfter=3)
doc = SimpleDocTemplate(str(ROOT/"docs/tasarim-kararlari.pdf"), pagesize=A4, leftMargin=36, rightMargin=36, topMargin=30, bottomMargin=24)
el = [Paragraph("Tasarım kararları notu", ParagraphStyle("t", fontName="DVS", fontSize=16, leading=20, spaceAfter=4)),
      P("Türkiye'de sosyal ağ kullanımı (Eurostat 2014–2025) · Hedef kitle: veri hikâyelerine meraklı genel okur ve işe alım yapanlar.")]
el.append(Paragraph("Renk", H2))
rows = [[P("<b>Renk</b>"), P("<b>Kullanım</b>"), P("<b>Gerekçe</b>")]]
for hx, use, why in [(ACC, "Vurgu: yalnızca Türkiye (çizgi, çubuk, işaret)", f"Portfolyodaki pudra-gül vurgusu; böylece iki site aynı kimliği taşır. Tüm grafiklerde aynı anlamı taşır; açıklığı griden belirgin biçimde ayrışır (renk körlüğünde de seçilir). Grafik öğesi olarak arka plana kontrast {cr(ACC, BG):.1f}:1 (≥3:1)."),
                     (ACCT, "Vurgu rengiyle yazılan metin", f"Metin için biraz açıldı: {cr(ACCT, BG):.1f}:1 (WCAG AA ≥4,5:1)."),
                     (BG, "Sayfa zemini (koyu tema)", f"Portfolyodaki koyu temanın devamı; açık metin ve pudra vurgu bu zeminde okunur. Kart yüzeyi {CARD}."),
                     (INK, "Gövde metni, seçilen ülke", f"{cr(INK, BG):.1f}:1. Sıcak beyaz; vurguyu öne çıkarır."),
                     (MUT, "İkincil metin, AB-27 çizgisi (kesikli)", f"{cr(MUT, BG):.1f}:1. Çizgi türü (kesikli) ve doğrudan etiket renge ek ipucu verir."),
                     (GRY, "Diğer ülkeler (bağlam)", "Gri ton: bağlam olarak okunur, dikkati dağıtmaz.")]:
    rows.append([P(f"<font color='{hx}'><b>■ {hx}</b></font>"), P(use), P(why)])
t = Table(rows, colWidths=[62, 170, 290]); t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .4, "#bbbbbb"), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, 0), "#eeeae0"), ("BACKGROUND", (0, 1), (0, -1), BG)])); el.append(t)
el.append(P("Gökkuşağı skalası yok; tek vurgu + nötr tonlar. Renk tek başına bilgi taşımaz: Türkiye ayrıca ▶ işareti, kalın etiket ve doğrudan etiketle belirtilir."))
el.append(Paragraph("Tipografi", H2))
el.append(P("<b>Başlıklar:</b> Georgia (serif, sistem yazı tipi), bulgu cümlesi biçiminde; hikâyeye editoryal bir ses verir. <b>Gövde ve grafik etiketleri:</b> sistem sans-serif (system-ui). Toplam 2 aile; harici yazı tipi yüklenmediği için performans etkilenmez. "
            "<b>Gövde</b> 18 px (mobilde 17 px, ≥16 px), satır aralığı 1,6, satır uzunluğu ~40 rem ≈ 65–70 karakter. Hiyerarşi: kicker → H1 (en çok 3,5 rem) → H2 → grafik başlığı H3 → gövde → kaynak notu (0,9 rem)."))
el.append(Paragraph("Grafik seçimleri", H2))
rows = [[P("<b>Soru</b>"), P("<b>Grafik</b>"), P("<b>Neden</b>")],
 [P("Zaman içinde değişim (sabit grafik)"), P("Çizgi grafik"), P("Zaman için standart; 7 adımda vurgulama, ekleme ve açıklama ile okuyucu neye bakacağını bilir. Eksen 30'dan başlar (çubuk değil, çizgi); eksen etiketli.")],
 [P("Ülkeleri karşılaştırma"), P("Sıralı yatay çubuk"), P("Uzun ülke adları yatay okunur; sıfırdan başlar; AB-27 kesikli referans çizgisi. Yıl kaydırıcısı ile okuyucu zamanı seçer; mobilde 13 satıra sadeleşir.")],
 [P("İki değişken ilişkisi"), P("Saçılım + eğilim çizgisi"), P("Başlangıç düzeyi ile artış arasındaki ilişkiyi gösterir; korelasyon nedensellik gibi sunulmaz.")],
 [P("Okuyucu keşfi"), P("Çizgi + iki seçim kutusu"), P("Tooltip değil, gerçek kontrol; klavyeyle kullanılır, başlık seçime göre güncellenir (aria-live).")]]
t = Table(rows, colWidths=[110, 100, 312]); t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .4, "#bbbbbb"), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, 0), "#eeeae0")])); el.append(t)
el.append(P("Kaçınılanlar: 3B, çift eksen, pasta grafik, harita (ham sayı), gökkuşağı. Her grafikte bulgu cümlesi başlığı, eksen etiketi, birim, kaynak notu ve açıklamalar var."))
el.append(Paragraph("Duyarlılık ve erişilebilirlik", H2))
el.append(P("360 / 768 / 1280 px'te test edildi, yatay kaydırma yok. Masaüstünde grafik sağda sabit, metin solda; mobilde grafik üstte sabit (ekranın %56'sı), metin altından akar. Anlamlı HTML (header, main, section, figure, figcaption), atlama bağlantısı, her grafikte aria-label, "
            "<font name='DVB'>prefers-reduced-motion</font> desteği, kontrollerde ≥44 px dokunma alanı ve görünür odak halkası. Lighthouse mobil: Performans 99, Erişilebilirlik 100, En İyi Uygulamalar 100, SEO 100."))
doc.build(el)
print("tamam")
