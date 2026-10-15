"use strict";
/* Tüm değerler data/summary.json ve data/facts.json dosyalarından okunur (notebooks/analiz.ipynb üretir). */
const $ = s => document.querySelector(s);
const EU = "AB-27 ortalaması", TRK = "Türkiye";
const ACC = "#EBA8BB", INK = "#f5ecef", MUT = "#c2b2ba", GRY = "#8f808a", ACCT = "#F2BDCB";
let D, F, cur = 0;

const num = (v, dp = 1) => v.toFixed(dp).replace(".", ",").replace("-", "−");
const fx = k => { const v = F[k]; return k === "r" ? num(v, 2) : Number.isInteger(v) ? String(v) : num(v, 1); };
const T = s => s.replace(/\{(\w+)\}/g, (_, k) => fx(k));
const svg = (w, h, label, inner) => `<svg viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" role="img" aria-label="${label}">${inner}</svg>`;
const dims = el => { const w = Math.max(300, el.clientWidth); return { w, h: Math.round(Math.min(460, Math.max(300, w * .7))) }; };
const lab = (x, y, t, attr) => t.split("|").map((p, i) => `<text x="${x}" y="${y + i * 14}" ${attr}>${p}</text>`).join("");
const last = () => D.years.length - 1;

Promise.all(["data/summary.json", "data/facts.json"].map(u => fetch(u).then(r => r.json())))
  .then(([d, f]) => { D = d; F = f; init(); });

/* ---------- Çizgi grafik (hem sabit hem keşif grafiği) ---------- */
function line(el, o, label) {
  const { w, h } = dims(el), m = { l: 38, r: 84, t: 26, b: 30 }, Y = D.years, n = Y.length, lim = o.upto == null ? n - 1 : o.upto;
  const x = i => m.l + i * (w - m.l - m.r) / (n - 1), y = v => m.t + (1 - (v - 30) / 70) * (h - m.t - m.b);
  let s = `<text x="${m.l}" y="12">Kullanıcı oranı (%)</text>`;
  for (let v = 30; v <= 100; v += 10) s += `<line class="grid" x1="${m.l}" x2="${w - m.r}" y1="${y(v)}" y2="${y(v)}"/><text x="${m.l - 6}" y="${y(v) + 4}" text-anchor="end">${v}</text>`;
  Y.forEach((yr, i) => { if (i % (w < 520 ? 3 : 1) === 0) s += `<text x="${x(i)}" y="${h - 10}" text-anchor="middle">${yr}</text>`; });
  s += `<text x="${(m.l + w - m.r) / 2}" y="${h - 0}" text-anchor="middle" style="font-size:0">Yıl</text>`;
  o.series.forEach(se => {
    let d = "", pen = false, li = -1;
    se.v.forEach((v, i) => { if (i > lim || v == null) { pen = false; return; } d += (pen ? "L" : "M") + x(i).toFixed(1) + " " + y(v).toFixed(1); pen = true; li = i; });
    s += `<path d="${d}" fill="none" stroke="${se.c}" stroke-width="${se.sw || 2.5}"${se.dash ? ` stroke-dasharray="${se.dash}"` : ""}/>`;
    if (li >= 0) s += `<circle cx="${x(li)}" cy="${y(se.v[li])}" r="3.5" fill="${se.c}"/><text x="${x(li) + 7}" y="${y(se.v[li]) + 4}" style="fill:${se.tc || se.c};font-weight:700">${se.l}</text>`;
  });
  (o.annos || []).forEach(a => {
    const se = o.series.find(q => q.k === a.k), v = se.v[a.i]; if (v == null) return;
    s += `<circle cx="${x(a.i)}" cy="${y(v)}" r="6" fill="none" stroke="${INK}" stroke-width="2"/>` + lab(x(a.i) + (a.dx || 0), y(v) + (a.dy ?? -14), T(a.t), `class="an" text-anchor="${a.a || "middle"}"`);
  });
  el.innerHTML = svg(w, h, label, s);
}
const S = () => ({
  eu: { k: "eu", l: "AB-27", v: D.series[EU], c: MUT, dash: "6 4" },
  tr: { k: "tr", l: TRK, v: D.series[TRK], c: ACC, tc: ACCT, sw: 3.5 },
  dk: { k: "dk", l: "Danimarka", v: D.series["Danimarka"], c: GRY, tc: MUT, sw: 2 },
  it: { k: "it", l: "İtalya", v: D.series["İtalya"], c: GRY, tc: MUT, sw: 2 }
});

/* ---------- Scrollytelling adımları (metinler şablon; sayılar facts.json'dan) ---------- */
function steps() {
  const s = S(), L = last();
  return [
    { t: "AB'de 2014'te her 10 kişiden yaklaşık 4'ü sosyal ağdaydı", p: "2014'te AB'de 16–74 yaş arasındaki her 10 kişiden yaklaşık 4'ü sosyal ağ kullanıyordu (%{eu14}).", s: [s.eu], u: 0, a: [{ k: "eu", i: 0, t: "2014: %{eu14}", a: "start", dx: 8, dy: -12 }] },
    { t: "AB ortalaması 11 yılda {eu_delta} puan arttı", p: "2025'te oran %{eu25}'e çıktı: {eu_delta} puanlık artış. Artık yaklaşık her 3 kişiden 2'si ağda.", s: [s.eu], a: [{ k: "eu", i: L, t: "2025: %{eu25}", a: "end", dx: -6, dy: -14 }] },
    { t: "Türkiye 2014'te AB ortalamasının altında başladı", p: "Türkiye 2014'te %{tr14} ile AB ortalamasının yaklaşık {gap14} puan altındaydı.", s: [s.eu, s.tr], u: 0, a: [{ k: "tr", i: 0, t: "Türkiye %{tr14}|AB'nin ~{gap14} puan altı", a: "start", dx: 10, dy: 26 }] },
    { t: "Türkiye {cross_year}'de AB ortalamasını geçti", p: "{cross_year}'de Türkiye AB ortalamasını geçti (%{cross_tr} ve %{cross_eu}) ve bir daha altına inmedi.", s: [s.eu, s.tr], u: F.cross_i, a: [{ k: "tr", i: F.cross_i, t: "{cross_year}: geçiş", dy: -16 }] },
    { t: "2021'de Türkiye'de artış durdu", p: "2021'de artış durdu: oran %{tr20}'den %{tr21}'e geriledi. Nedenini bu veriyle söyleyemeyiz.", s: [s.eu, s.tr], u: F.i21, a: [{ k: "tr", i: F.i21, t: "2021: %{tr21}|(2020'de %{tr20})", dy: -30 }] },
    { t: "2022'de tek yılda {jump} puanlık sıçrama", p: "Ardından tek yılda {jump} puanlık sıçrama geldi: 2022'de oran %{tr22} oldu.", s: [s.eu, s.tr], u: F.i22, a: [{ k: "tr", i: F.i22, t: "+{jump} puan", a: "end", dx: -10, dy: -8 }] },
    { t: "2025'te Türkiye AB ortalamasının yaklaşık {gap25} puan üstünde", p: "2025'te Türkiye %{tr25} ile AB ortalamasının yaklaşık {gap25} puan üstünde. Danimarka'ya (%{dk25}) yetişmedi, İtalya'nın (%{it25}) ise çok ilerisinde.", s: [s.eu, s.tr, s.dk, s.it], a: [{ k: "tr", i: L, t: "%{tr25}", a: "end", dx: -8, dy: -12 }] }
  ];
}
function drawStep() { const st = steps()[cur], t = T(st.t); $("#t1").textContent = t; line($("#c1"), { series: st.s, upto: st.u, annos: st.a }, "Çizgi grafik: " + t); }

/* ---------- Yatay çubuk grafik + yıl kaydırıcısı ---------- */
function bars() {
  const el = $("#c2"), w = Math.max(300, el.clientWidth), yr = +$("#yr").value, yi = yr - D.years[0], mob = w < 520;
  $("#yro").textContent = yr;
  const rows = Object.entries(D.series).filter(([c, v]) => c !== EU && v[yi] != null).map(([c, v]) => [c, v[yi]]).sort((a, b) => b[1] - a[1]).map((r, i) => [...r, i + 1]);
  const n = rows.length, tr = rows.find(r => r[0] === TRK), eu = D.series[EU][yi], d = Math.abs(tr[1] - eu);
  let view = rows;
  if (mob) { const keep = new Set([...rows.slice(0, 10), tr, ...rows.slice(-2)].map(r => r[0])); view = rows.filter(r => keep.has(r[0])); }
  $("#mn").hidden = !mob;
  const t = `${yr}: Türkiye ${n} ülke arasında ${tr[2]}. sırada, AB-27 ortalamasının ${num(d)} puan ${tr[1] >= eu ? "üstünde" : "altında"}`;
  $("#t2").textContent = t;
  const rh = mob ? 22 : 22, m = { l: mob ? 112 : 140, r: 46, t: 24, b: 38 }, h = m.t + m.b + view.length * rh, x = v => m.l + v / 100 * (w - m.l - m.r);
  let s = "";
  for (let v = 0; v <= 100; v += 20) s += `<line class="grid" x1="${x(v)}" x2="${x(v)}" y1="${m.t}" y2="${h - m.b}"/><text x="${x(v)}" y="${h - 22}" text-anchor="middle">${v}</text>`;
  s += `<text x="${(m.l + w - m.r) / 2}" y="${h - 6}" text-anchor="middle">Kullanıcı oranı (%, ${yr})</text>`;
  view.forEach(([c, v, rk], i) => {
    const isT = c === TRK, yy = m.t + i * rh, st = isT ? 'style="fill:' + ACCT + ';font-weight:700"' : "";
    s += `<text x="${m.l - 6}" y="${yy + 15}" text-anchor="end" ${st}>${isT ? "▶ " : ""}${rk}. ${c}</text><rect x="${m.l}" y="${yy + 3}" width="${Math.max(0, x(v) - m.l)}" height="${rh - 6}" fill="${isT ? ACC : GRY}"/><text class="an" x="${x(v) + 4}" y="${yy + 15}" ${isT ? st : 'style="font-weight:400"'}>${num(v)}</text>`;
  });
  s += `<line x1="${x(eu)}" x2="${x(eu)}" y1="${m.t - 4}" y2="${h - m.b}" stroke="${MUT}" stroke-width="2" stroke-dasharray="6 4"/><text class="an" x="${x(eu)}" y="12" text-anchor="middle">AB-27: %${num(eu)}</text>`;
  el.innerHTML = svg(w, h, `Yatay çubuk grafik: ${yr} yılında ${n} ülkenin sosyal ağ kullanım oranı. ${t}. En yüksek: ${rows[0][0]} %${num(rows[0][1])}; en düşük: ${rows[n - 1][0]} %${num(rows[n - 1][1])}.`, s);
}

/* ---------- Saçılım grafiği ---------- */
function scatter() {
  const el = $("#c3"), { w, h } = dims(el), m = { l: 44, r: 16, t: 24, b: 44 }, P = D.scatter;
  const xs = P.map(p => p.x), ys = P.map(p => p.y);
  const x0 = Math.floor(Math.min(...xs) / 10) * 10, x1 = Math.ceil(Math.max(...xs) / 10) * 10, y1 = Math.ceil(Math.max(...ys) / 10) * 10;
  const x = v => m.l + (v - x0) / (x1 - x0) * (w - m.l - m.r), y = v => h - m.b - v / y1 * (h - m.t - m.b);
  $("#t3").textContent = `2014'te düşük başlayan ülkeler 2025'e kadar daha çok yükseldi (r = ${num(F.r, 2)})`;
  let s = `<text x="${m.l}" y="12">Değişim 2014–2025 (puan)</text>`;
  for (let v = 0; v <= y1; v += 10) s += `<line class="grid" x1="${m.l}" x2="${w - m.r}" y1="${y(v)}" y2="${y(v)}"/><text x="${m.l - 6}" y="${y(v) + 4}" text-anchor="end">${v}</text>`;
  for (let v = x0; v <= x1; v += 10) s += `<text x="${x(v)}" y="${h - 26}" text-anchor="middle">${v}</text>`;
  s += `<text x="${(m.l + w - m.r) / 2}" y="${h - 8}" text-anchor="middle">2014'te kullanıcı oranı (%)</text>`;
  const n = P.length, mx = xs.reduce((a, b) => a + b) / n, my = ys.reduce((a, b) => a + b) / n;
  const b = P.reduce((a, p) => a + (p.x - mx) * (p.y - my), 0) / P.reduce((a, p) => a + (p.x - mx) ** 2, 0), a0 = my - b * mx, xa = Math.min(...xs), xb = Math.max(...xs);
  s += `<line x1="${x(xa)}" y1="${y(a0 + b * xa)}" x2="${x(xb)}" y2="${y(a0 + b * xb)}" stroke="${MUT}" stroke-width="1.5" stroke-dasharray="6 4"/>`;
  P.forEach(p => { const t = p.c === TRK; s += t ? `<polygon points="${x(p.x)},${y(p.y) - 9} ${x(p.x) + 9},${y(p.y) + 7} ${x(p.x) - 9},${y(p.y) + 7}" fill="${ACC}"/>` : `<circle cx="${x(p.x)}" cy="${y(p.y)}" r="5" fill="${GRY}" fill-opacity=".85"/>`; });
  const srt = [...P].sort((a, c) => c.y - a.y), pick = new Set([TRK, srt.find(p => p.c !== TRK).c, srt[srt.length - 1].c, srt[srt.length - 2].c]);
  P.filter(p => pick.has(p.c)).forEach(p => {
    const right = p.x > (x0 + x1) / 2, isT = p.c === TRK, top = !isT && p === srt[0];
    if (isT) s += lab(x(p.x) + 14, y(p.y) - 2, `Türkiye|+${num(p.y)} puan`, 'class="an" text-anchor="start"');
    else if (top) s += lab(x(p.x) - 4, y(p.y) - 12, p.c, 'class="an" text-anchor="start"');
    else s += lab(x(p.x) + (right ? -12 : 12), y(p.y) + 4, p.c, `class="an" text-anchor="${right ? "end" : "start"}"`);
  });
  s += `<text x="${w - m.r}" y="${y(a0 + b * xb) - 8}" text-anchor="end">eğilim çizgisi</text>`;
  el.innerHTML = svg(w, h, `Saçılım grafiği: 2014 düzeyi ile 2014–2025 artışı arasında negatif ilişki, r ${num(F.r, 2)}. Türkiye ${num(P.find(p => p.c === TRK).y)} puan artışla en çok artan ülkelerden biri; ${srt[0].c} en çok, ${srt[srt.length - 1].c} en az artan.`, s);
}

/* ---------- Okuyucu keşfi: iki ülke seçimi ---------- */
function explore() {
  const A = $("#selA").value, B = $("#selB").value, d = S();
  const delta = c => { const v = D.series[c], q = v.filter(z => z != null), i0 = v.indexOf(q[0]), i1 = v.lastIndexOf(q[q.length - 1]); return [q[q.length - 1] - q[0], D.years[i1] - D.years[i0]]; };
  const se = [d.eu, d.tr]; const add = (c, st) => { if (c && c !== TRK) se.push({ k: c, l: c, v: D.series[c], ...st }); };
  add(A, { c: INK, sw: 2.5 }); add(B, { c: INK, sw: 3, dash: "2 4" });
  const [a, yrs] = delta(A), sg = v => (v >= 0 ? "+" : "") + num(v);
  $("#t4").textContent = `${A}: ${yrs} yılda ${sg(a)} puan` + (B ? `, ${B}: ${sg(delta(B)[0])} puan` : "") + `; Türkiye ${sg(F.tr_delta)}, AB-27 ${sg(F.eu_delta)} puan (2014–2025)`;
  const br = [A, B].filter(Boolean).filter(c => D.breaks[c]).map(c => `${c} ${D.breaks[c].join(", ")}`);
  $("#cap4").textContent = "Kaynak: Eurostat, tin00127 (erişim: 12.10.2026). Dikey eksen 30'dan başlar (çizgi grafik). Çizgideki boşluk, o yıl verinin olmadığını gösterir." + (br.length ? " Yöntem değişikliği (kesinti) yılları: " + br.join("; ") + "." : "");
  line($("#c4"), { series: se }, `Çizgi grafik: ${[A, B].filter(Boolean).join(" ve ")}, Türkiye ve AB-27 ortalamasının 2014–2025 sosyal ağ kullanım oranları. ${$("#t4").textContent}`);
}

function init() {
  document.querySelectorAll("[data-k]").forEach(e => { e.textContent = (e.hasAttribute("data-pct") ? "%" : "") + fx(e.dataset.k); });
  const names = Object.keys(D.series).filter(k => k !== EU).sort((a, b) => a.localeCompare(b, "tr"));
  names.forEach(k => $("#selA").add(new Option(k, k))); $("#selB").add(new Option("— yok —", "")); names.forEach(k => $("#selB").add(new Option(k, k)));
  $("#selA").value = "Almanya"; $("#selA").onchange = $("#selB").onchange = explore; $("#yr").oninput = bars;
  $("#steps").innerHTML = steps().map(s => `<div class="step"><p>${T(s.p)}</p></div>`).join("");
  const els = [...document.querySelectorAll(".step")];
  const mobile = matchMedia("(max-width:800px)").matches;
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { els.forEach(z => z.classList.remove("on")); e.target.classList.add("on"); cur = els.indexOf(e.target); drawStep(); } }),
    { rootMargin: mobile ? "-62% 0px -18% 0px" : "-45% 0px -45% 0px" });
  els.forEach(e => io.observe(e));
  const all = () => { drawStep(); bars(); scatter(); explore(); };
  all();
  let tm; addEventListener("resize", () => { clearTimeout(tm); tm = setTimeout(all, 150); });
}
