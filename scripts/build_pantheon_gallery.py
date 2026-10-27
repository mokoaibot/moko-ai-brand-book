#!/usr/bin/env python3
"""Build pantheon.html from the owner-provided SVG pool.

The script never edits artwork. It only enumerates the exact files stored under
assets/svg/pantheon and creates a static gallery with download links.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets" / "svg" / "pantheon"
OUTPUT = ROOT / "pantheon.html"

COLLECTIONS = (
    ("pantheon-svg", "Основной пул", "30 SVG · 10 образов × 3 варианта"),
    ("pantheon-svg-batch-2/amun", "Амун", "3 дополнительных варианта"),
    ("pantheon-svg-batch-2/aset", "Асет", "3 дополнительных варианта"),
    ("pantheon-svg-batch-2/bold-01", "Bold 01", "12 образов"),
    ("pantheon-svg-batch-2/bold-02", "Bold 02", "12 образов"),
    ("pantheon-svg-batch-2/bold-03", "Bold 03", "12 образов"),
    ("pantheon-svg-batch-2/faceted-01", "Faceted 01", "12 образов"),
    ("pantheon-svg-batch-2/minimal-01", "Minimal 01", "12 образов"),
    ("pantheon-svg-batch-2/minimal-02", "Minimal 02", "12 образов"),
    ("pantheon-svg-batch-2/minimal-03", "Minimal 03", "12 образов"),
)

DEITIES = {
    "amun": "Амун",
    "anubis": "Анубис",
    "aset": "Асет",
    "bastet": "Бастет",
    "hathor": "Хатхор",
    "horus": "Гор",
    "isis": "Исида",
    "maat": "Маат",
    "osiris": "Осирис",
    "ra": "Ра",
    "sekhmet": "Сехмет",
    "set": "Сет",
    "thoth": "Тот",
}


def title_for(stem: str) -> str:
    parts = stem.rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return f"{DEITIES.get(parts[0], parts[0].title())} {parts[1]}"
    return DEITIES.get(stem, stem.title())


def card(path: Path, collection: str, eager: bool = False) -> str:
    relative = path.relative_to(ASSET_ROOT).as_posix()
    stem = path.stem
    title = title_for(stem)
    svg = f"assets/svg/pantheon/{relative}"
    export_base = f"pantheon/{Path(relative).with_suffix('').as_posix()}"
    loading = "eager" if eager else "lazy"
    return f'''      <article class="card">
        <a class="stage" href="{svg}" aria-label="Открыть SVG: {escape(title)}"><img src="{svg}" loading="{loading}" decoding="async" alt="{escape(title)} — подготовленный SVG из пула Пантеона"></a>
        <div class="card-head"><h3>{escape(title)}</h3><span class="format">SVG</span></div>
        <div class="role">{escape(collection.upper())}</div>
        <div class="file"><code>{escape(relative)}</code><span class="actions"><a class="btn" href="{svg}" download>SVG</a><a class="btn" href="exports/png/{export_base}.png" download>PNG</a><a class="btn" href="exports/jpg/{export_base}.jpg" download>JPG</a><a class="btn" href="exports/webp/{export_base}.webp" download>WEBP</a></span></div>
      </article>'''


def main() -> None:
    groups: list[tuple[str, str, str, list[Path]]] = []
    all_files: list[Path] = []
    for relative_dir, label, note in COLLECTIONS:
        files = sorted((ASSET_ROOT / relative_dir).glob("*.svg"))
        if not files:
            raise SystemExit(f"No SVG files in {relative_dir}")
        groups.append((relative_dir, label, note, files))
        all_files.extend(files)

    if len(all_files) != 120:
        raise SystemExit(f"Expected 120 SVG assets, found {len(all_files)}")

    nav = "".join(
        f'<a href="#{relative_dir.replace("/", "-")}">{escape(label)} <span>{len(files)}</span></a>'
        for relative_dir, label, _note, files in groups
    )
    sections = []
    card_index = 0
    for index, (relative_dir, label, note, files) in enumerate(groups, start=1):
        section_id = relative_dir.replace("/", "-")
        cards = []
        for path in files:
            cards.append(card(path, label, eager=card_index < 4))
            card_index += 1
        sections.append(f'''    <section class="collection" id="{section_id}">
      <div class="wrap">
        <div class="section-head"><div class="num">{index:02d} / {len(files):03d}</div><div><h2>{escape(label)}</h2><p>{escape(note)} · исходные имена сохранены</p></div></div>
        <div class="grid">
{chr(10).join(cards)}
        </div>
      </div>
    </section>''')

    hero_svg = "assets/svg/pantheon/pantheon-svg/anubis-01.svg"
    html = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Пантеон MOKO AI: полный подготовленный пул из 120 SVG-ассетов, загруженный из папки ПАНТЕОН владельца.">
  <title>Пантеон MOKO AI — 120 подготовленных SVG</title>
  <style>
    @font-face{{font-family:Jost;src:url("assets/fonts/jost/Jost-Variable.ttf") format("truetype");font-weight:100 900;font-display:swap}}
    @font-face{{font-family:Inter;src:url("assets/fonts/inter/Inter-Variable.ttf") format("truetype");font-weight:100 900;font-display:swap}}
    :root{{--red:#d64545;--red-light:#f56a6a;--black:#050505;--panel:#0a0a0a;--panel-2:#111314;--dim:#6b7177;--grey:#9ca3af;--white:#fff;--max:1320px}}
    *{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--black);color:var(--white);font:15px/1.55 Inter,Arial,sans-serif}}body:before{{content:"";display:block;height:5px;background:var(--red)}}img{{display:block;max-width:100%}}a{{color:inherit}}code,.mono{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}.wrap{{width:min(calc(100% - 40px),var(--max));margin:auto}}
    nav{{position:sticky;top:0;z-index:10;border-bottom:1px solid rgba(255,255,255,.1);background:rgba(5,5,5,.96);backdrop-filter:blur(12px)}}.nav{{min-height:66px;display:flex;align-items:center;justify-content:space-between;gap:24px}}.brand{{display:flex;align-items:center;gap:14px;text-decoration:none}}.brand img{{width:190px}}.brand span{{padding-left:14px;border-left:1px solid rgba(255,255,255,.18);color:var(--grey);font:10px ui-monospace,monospace;letter-spacing:.12em}}.links{{display:flex;gap:20px}}.links a{{color:var(--grey);font-size:12px;text-decoration:none}}.links a:hover,.links a[aria-current="page"]{{color:var(--white)}}
    .hero{{padding:72px 0;border-bottom:1px solid rgba(255,255,255,.1)}}.hero-grid{{display:grid;grid-template-columns:1fr minmax(320px,470px);gap:72px;align-items:center}}.eyebrow{{margin:0 0 14px;color:var(--red);font:700 11px/1.2 ui-monospace,monospace;letter-spacing:.16em}}h1,h2,h3{{font-family:Jost,Arial,sans-serif}}h1{{margin:0;font-size:clamp(58px,9vw,104px);font-weight:600;line-height:.88;letter-spacing:-.055em}}.lead{{max-width:700px;margin:24px 0 0;color:var(--grey);font-size:17px}}.facts{{display:flex;flex-wrap:wrap;gap:8px;margin-top:28px}}.fact{{padding:7px 10px;border:1px solid rgba(255,255,255,.14);border-radius:8px;color:var(--grey);font-size:11px}}.hero-mark{{padding:20px;border:1px solid rgba(255,255,255,.1);border-radius:30px;background:var(--panel)}}.hero-mark img{{width:100%;aspect-ratio:1;object-fit:contain}}.caption{{display:flex;justify-content:space-between;gap:14px;margin-top:10px;color:var(--dim);font:10px ui-monospace,monospace}}
    .pool-nav{{padding:20px 0;border-bottom:1px solid rgba(255,255,255,.1);background:#080808}}.pool-links{{display:flex;flex-wrap:wrap;gap:8px}}.pool-links a{{padding:8px 10px;border:1px solid rgba(255,255,255,.12);border-radius:8px;color:var(--grey);font-size:11px;text-decoration:none}}.pool-links a:hover{{border-color:var(--red);color:var(--white)}}.pool-links span{{color:var(--red)}}
    section{{padding:68px 0;border-bottom:1px solid rgba(255,255,255,.1);scroll-margin-top:66px}}.section-head{{display:grid;grid-template-columns:100px 1fr;gap:18px;align-items:start;margin-bottom:28px}}.section-head p{{margin:8px 0 0;color:var(--grey)}}.num{{padding-top:8px;color:var(--red);font:11px ui-monospace,monospace;letter-spacing:.12em}}h2{{margin:0;font-size:clamp(36px,5vw,54px);font-weight:600;line-height:1;letter-spacing:-.03em}}.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}}.card{{min-width:0;padding:14px;border:1px solid rgba(255,255,255,.1);border-radius:16px;background:var(--panel)}}.card-head{{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:13px}}.card h3{{margin:0;font-size:21px;font-weight:600}}.format{{padding:3px 6px;border:1px solid rgba(255,255,255,.13);border-radius:5px;color:var(--dim);font:9px ui-monospace,monospace}}.role{{margin:2px 0 0;color:var(--red);font:700 9px ui-monospace,monospace;letter-spacing:.1em}}.stage{{min-height:232px;display:grid;place-items:center;overflow:hidden;border-radius:11px;background:var(--panel-2)}}.stage img{{width:min(94%,238px);height:220px;object-fit:contain}}.file{{display:grid;gap:10px;margin-top:12px;padding-top:11px;border-top:1px solid rgba(255,255,255,.08)}}.file code{{min-height:28px;color:var(--dim);font-size:9px;overflow-wrap:anywhere}}.actions{{display:flex;flex-wrap:wrap;gap:5px}}.btn{{flex:none;padding:6px 8px;border:1px solid rgba(255,255,255,.18);border-radius:7px;text-decoration:none;font-size:9px;font-weight:700}}.btn:hover{{border-color:var(--red)}}
    .provenance{{padding:70px 0}}.specs{{margin:0;border:1px solid rgba(255,255,255,.1);border-radius:16px;overflow:hidden}}.spec{{display:grid;grid-template-columns:220px 1fr;gap:20px;padding:16px 19px;background:var(--panel);border-bottom:1px solid rgba(255,255,255,.08)}}.spec:last-child{{border-bottom:0}}.spec dt{{color:var(--grey)}}.spec dd{{margin:0}}.note{{margin-top:18px;padding:18px 20px;border-left:3px solid var(--red);border-radius:0 12px 12px 0;background:var(--panel);color:var(--grey);font-size:13px}}.note strong{{color:var(--white)}}footer{{padding:40px 0 60px;color:var(--dim);font-size:11px}}.footer{{display:flex;justify-content:space-between;gap:20px}}
    @media(max-width:1120px){{.grid{{grid-template-columns:repeat(3,minmax(0,1fr))}}}}@media(max-width:940px){{.hero-grid{{grid-template-columns:1fr}}.hero-mark{{max-width:480px}}.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}@media(max-width:650px){{.wrap{{width:min(calc(100% - 28px),var(--max))}}.links{{display:none}}.brand span{{display:none}}.hero,section{{padding:52px 0}}.section-head{{grid-template-columns:1fr;gap:8px}}.grid{{grid-template-columns:1fr}}.spec{{grid-template-columns:1fr;gap:4px}}.footer{{flex-direction:column}}}}
  </style>
</head>
<body>
  <nav aria-label="Разделы страницы"><div class="wrap nav"><a class="brand" href="index.html" aria-label="Вернуться в брендбук MOKO AI"><img src="assets/svg/logo/moko-ai-horus-horizontal-dark.svg" alt="MOKO AI"><span>ПАНТЕОН</span></a><div class="links"><a href="index.html">Брендбук</a><a href="#collection" aria-current="page">Коллекции</a><a href="#source">Источник</a></div><span class="mono" style="color:var(--dim);font-size:10px">120 / 120</span></div></nav>
  <main id="top">
    <header class="hero"><div class="wrap hero-grid"><div><p class="eyebrow">ПОЛНЫЙ ПОДГОТОВЛЕННЫЙ ПУЛ · GOOGLE DRIVE</p><h1>Пантеон</h1><p class="lead">Все 120 SVG из папки «ПАНТЕОН» владельца. Исходные файлы опубликованы без перерисовки, отбора и переименования.</p><div class="facts"><span class="fact">120 исходных SVG</span><span class="fact">10 папок коллекций</span><span class="fact">Имена и структура сохранены</span><span class="fact">SVG · PNG · JPG · WEBP</span></div></div><figure class="hero-mark"><img src="{hero_svg}" alt="Анубис 01 — подготовленный SVG из пула Пантеона"><figcaption class="caption"><span>PANTHEON-SVG / ANUBIS-01</span><span>ИЗ ПАПКИ ВЛАДЕЛЬЦА</span></figcaption></figure></div></header>
    <div class="pool-nav" id="collection"><div class="wrap pool-links">{nav}</div></div>
{chr(10).join(sections)}
    <section class="provenance" id="source"><div class="wrap"><div class="section-head"><div class="num">SOURCE</div><div><h2>Источник и целостность</h2><p>Опубликованный пул полностью соответствует скачанному набору.</p></div></div><dl class="specs"><div class="spec"><dt>Источник</dt><dd>Google Drive · папка «ПАНТЕОН» · ID <code>1EDzc6O5Hoxfymjmn9axY5zs9vJ9nJRVg</code></dd></div><div class="spec"><dt>Состав</dt><dd>120 SVG-файлов, 1 787 320 байт, 10 каталогов коллекций.</dd></div><div class="spec"><dt>Целостность</dt><dd>Исходные имена, каталоги и байты SVG сохранены. Контрольные суммы записаны в <code>assets/svg/pantheon/manifest.csv</code>.</dd></div><div class="spec"><dt>Веб-форматы</dt><dd>Для каждого SVG подготовлены PNG, JPG и lossless WebP с сохранением структуры каталогов.</dd></div><div class="spec"><dt>Основной знак</dt><dd>Коллекция не изменяет утверждённый логотип Гора и его эталонный SVG.</dd></div></dl><div class="note"><strong>Важно:</strong> ранее самостоятельно созданные варианты удалены из активов, экспортов, страницы и сборочного процесса. На этой странице показаны только файлы из подготовленного пула владельца.</div></div></section>
  </main>
  <footer><div class="wrap footer"><span>MOKO AI Pantheon · 120 owner-provided SVG assets · 2026-10-27</span><span><a href="index.html">Вернуться в брендбук</a></span></div></footer>
</body>
</html>
'''
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Built {OUTPUT.name}: {len(groups)} collections, {len(all_files)} assets")


if __name__ == "__main__":
    main()
