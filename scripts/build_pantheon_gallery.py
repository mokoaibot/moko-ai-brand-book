#!/usr/bin/env python3
"""Build a human-readable Pantheon gallery from the owner-provided SVG pool.

The script never edits artwork. It only groups the exact files stored under
assets/svg/pantheon by deity and creates a static page with download links.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets" / "svg" / "pantheon"
OUTPUT = ROOT / "pantheon.html"

DEITIES = (
    {
        "key": "amun",
        "aliases": {"amun"},
        "name": "Амун",
        "role": "Скрытая сила и царская власть",
        "description": "Бог невидимой созидающей силы и покровитель царской власти. Его образ узнаётся по высоким перьям, короне и бараньим рогам.",
        "symbol": "перья и рога овна",
    },
    {
        "key": "anubis",
        "aliases": {"anubis"},
        "name": "Анубис",
        "role": "Проводник и хранитель некрополей",
        "description": "Покровитель погребальных обрядов и проводник в мир мёртвых. Главный визуальный знак — голова шакала с высокими ушами.",
        "symbol": "шакал",
    },
    {
        "key": "bastet",
        "aliases": {"bastet"},
        "name": "Бастет",
        "role": "Дом, радость и защита",
        "description": "Богиня домашнего очага, радости и мягкой защитной силы. Изображается как кошка или женщина с кошачьей головой.",
        "symbol": "кошка",
    },
    {
        "key": "hathor",
        "aliases": {"hathor"},
        "name": "Хатхор",
        "role": "Любовь, музыка и материнство",
        "description": "Богиня любви, музыки, красоты и материнства. Её традиционные знаки — коровьи рога, уши и солнечный диск.",
        "symbol": "рога и солнечный диск",
    },
    {
        "key": "horus",
        "aliases": {"horus"},
        "name": "Гор",
        "role": "Небо, защита и царская власть",
        "description": "Бог неба и защитник царской власти. Соколиная голова и глаз Гора передают зоркость, порядок и покровительство.",
        "symbol": "сокол и глаз Гора",
    },
    {
        "key": "isis",
        "aliases": {"isis", "aset"},
        "name": "Исида (Асет)",
        "role": "Материнство, магия и защита",
        "description": "Богиня материнства, магии и царской защиты. Узнаваема по тронному знаку, крыльям и солнечному диску между рогами.",
        "symbol": "трон, крылья и диск",
    },
    {
        "key": "maat",
        "aliases": {"maat"},
        "name": "Маат",
        "role": "Истина, порядок и равновесие",
        "description": "Богиня истины, справедливости и мирового порядка. Её главный символ — страусиное перо, знак меры и равновесия.",
        "symbol": "страусиное перо",
    },
    {
        "key": "osiris",
        "aliases": {"osiris"},
        "name": "Осирис",
        "role": "Возрождение и загробный мир",
        "description": "Бог возрождения и владыка загробного мира. В образе часто присутствуют корона атеф, посох и плеть.",
        "symbol": "корона атеф",
    },
    {
        "key": "ra",
        "aliases": {"ra"},
        "name": "Ра",
        "role": "Солнце и жизненная сила",
        "description": "Солнечный бог и источник жизненной силы. Его образ объединяет соколиную голову, солнечный диск и царственную осанку.",
        "symbol": "солнечный диск",
    },
    {
        "key": "sekhmet",
        "aliases": {"sekhmet"},
        "name": "Сехмет",
        "role": "Сила, война и исцеление",
        "description": "Львиноголовая богиня разрушительной силы и исцеления. Её узнаваемые признаки — черты львицы и солнечный диск.",
        "symbol": "львица и солнечный диск",
    },
    {
        "key": "set",
        "aliases": {"set"},
        "name": "Сет",
        "role": "Пустыня, буря и противостояние",
        "description": "Бог пустыни, бури и силы противостояния. Узнаётся по вытянутой морде и высоким прямым ушам мифического животного Сета.",
        "symbol": "животное Сета",
    },
    {
        "key": "thoth",
        "aliases": {"thoth"},
        "name": "Тот",
        "role": "Мудрость, письмо и счёт",
        "description": "Бог мудрости, письма, знания и счёта. Чаще всего изображается с головой ибиса и лунными символами.",
        "symbol": "ибис и луна",
    },
)

SERIES_LABELS = {
    "pantheon-svg": "Детализированный образ",
    "pantheon-svg-batch-2/amun": "Дополнительный образ",
    "pantheon-svg-batch-2/aset": "Дополнительный образ",
    "pantheon-svg-batch-2/bold-01": "Сильный силуэт",
    "pantheon-svg-batch-2/bold-02": "Пластичный силуэт",
    "pantheon-svg-batch-2/bold-03": "Монументальный силуэт",
    "pantheon-svg-batch-2/faceted-01": "Гранёная эмблема",
    "pantheon-svg-batch-2/minimal-01": "Лаконичный знак",
    "pantheon-svg-batch-2/minimal-02": "Чистый контур",
    "pantheon-svg-batch-2/minimal-03": "Знаковый силуэт",
}

SERIES_ORDER = {name: index for index, name in enumerate(SERIES_LABELS)}


def raw_deity(path: Path) -> str:
    stem = path.stem
    base, separator, suffix = stem.rpartition("-")
    if separator and suffix.isdigit():
        return base
    return stem


def deity_for(path: Path) -> dict[str, object]:
    raw = raw_deity(path)
    for deity in DEITIES:
        if raw in deity["aliases"]:
            return deity
    raise ValueError(f"Unknown deity in {path}")


def series_for(path: Path) -> str:
    relative_parent = path.parent.relative_to(ASSET_ROOT).as_posix()
    if relative_parent not in SERIES_LABELS:
        raise ValueError(f"Unknown collection folder: {relative_parent}")
    return relative_parent


def sort_key(path: Path) -> tuple[int, str]:
    return SERIES_ORDER[series_for(path)], path.name


def icon_for(key: str) -> Path:
    return ASSET_ROOT / "pantheon-svg-batch-2" / "minimal-03" / f"{key}.svg"


def links(path: Path) -> tuple[str, str, str, str]:
    relative = path.relative_to(ASSET_ROOT).as_posix()
    svg = f"assets/svg/pantheon/{relative}"
    base = f"pantheon/{Path(relative).with_suffix('').as_posix()}"
    return svg, f"exports/png/{base}.png", f"exports/jpg/{base}.jpg", f"exports/webp/{base}.webp"


def variant_card(path: Path, deity: dict[str, object], number: int) -> str:
    relative = path.relative_to(ASSET_ROOT).as_posix()
    label = SERIES_LABELS[series_for(path)]
    svg, png, jpg, webp = links(path)
    name = str(deity["name"])
    symbol = str(deity["symbol"])
    return f'''        <article class="card">
          <a class="stage" href="{svg}" aria-label="Открыть SVG: {escape(name)}, {escape(label.lower())}"><img src="{svg}" loading="lazy" decoding="async" alt="{escape(name)} — {escape(label.lower())}"></a>
          <div class="card-head"><h3>{escape(label)}</h3><span class="variant">Вариант {number} из 10</span></div>
          <p class="card-note">{escape(name)} · {escape(symbol)}</p>
          <div class="actions"><a class="btn primary" href="{svg}" download>Скачать SVG</a><a class="btn" href="{png}" download>PNG</a><a class="btn" href="{jpg}" download>JPG</a><a class="btn" href="{webp}" download>WebP</a></div>
          <details class="source-file"><summary>Исходное имя файла</summary><code>{escape(relative)}</code></details>
        </article>'''


def main() -> None:
    all_files = sorted(ASSET_ROOT.rglob("*.svg"))
    if len(all_files) != 120:
        raise SystemExit(f"Expected 120 SVG assets, found {len(all_files)}")

    grouped: dict[str, list[Path]] = {str(deity["key"]): [] for deity in DEITIES}
    for path in all_files:
        deity = deity_for(path)
        grouped[str(deity["key"])].append(path)
    for paths in grouped.values():
        paths.sort(key=sort_key)
    wrong = {key: len(paths) for key, paths in grouped.items() if len(paths) != 10}
    if wrong:
        raise SystemExit(f"Each deity must have 10 variants: {wrong}")

    overview_cards = []
    hero_icons = []
    sections = []
    for deity in DEITIES:
        key = str(deity["key"])
        name = str(deity["name"])
        role = str(deity["role"])
        description = str(deity["description"])
        symbol = str(deity["symbol"])
        icon = icon_for(key)
        if not icon.exists():
            raise SystemExit(f"Missing representative icon: {icon}")
        icon_url = f"assets/svg/pantheon/{icon.relative_to(ASSET_ROOT).as_posix()}"
        hero_icons.append(
            f'<img src="{icon_url}" loading="eager" decoding="async" alt="" aria-hidden="true">'
        )
        overview_cards.append(f'''      <a class="god-link" href="#god-{key}">
        <span class="god-icon"><img src="{icon_url}" loading="lazy" decoding="async" alt="Иконка: {escape(name)}"></span>
        <span><strong>{escape(name)}</strong><small>{escape(role)}</small></span>
      </a>''')

        cards = "\n".join(
            variant_card(path, deity, index)
            for index, path in enumerate(grouped[key], start=1)
        )
        sections.append(f'''    <section class="deity" id="god-{key}">
      <div class="wrap">
        <header class="deity-head">
          <div class="deity-icon"><img src="{icon_url}" loading="lazy" decoding="async" alt="Иконка: {escape(name)}"></div>
          <div><div class="section-kicker">10 ПОДГОТОВЛЕННЫХ ВАРИАНТОВ</div><h2>{escape(name)}</h2><p>{escape(description)}</p><div class="attributes"><span>{escape(role)}</span><span>Главный знак: {escape(symbol)}</span></div></div>
        </header>
        <div class="grid">
{cards}
        </div>
      </div>
    </section>''')

    html = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Пантеон MOKO AI: 12 египетских богов, краткие описания и полный набор из 120 подготовленных SVG-иконок.">
  <title>Пантеон MOKO AI — 12 богов и 120 иконок</title>
  <style>
    @font-face{{font-family:Jost;src:url("assets/fonts/jost/Jost-Variable.ttf") format("truetype");font-weight:100 900;font-display:swap}}
    @font-face{{font-family:Inter;src:url("assets/fonts/inter/Inter-Variable.ttf") format("truetype");font-weight:100 900;font-display:swap}}
    :root{{--red:#d64545;--red-light:#f56a6a;--black:#050505;--panel:#0a0a0a;--panel-2:#111314;--line:rgba(255,255,255,.1);--dim:#6b7177;--grey:#9ca3af;--white:#fff;--max:1320px}}
    *{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--black);color:var(--white);font:15px/1.55 Inter,Arial,sans-serif}}body:before{{content:"";display:block;height:5px;background:var(--red)}}img{{display:block;max-width:100%}}a{{color:inherit}}code,.mono{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}.wrap{{width:min(calc(100% - 40px),var(--max));margin:auto}}
    nav{{position:sticky;top:0;z-index:10;border-bottom:1px solid var(--line);background:rgba(5,5,5,.96);backdrop-filter:blur(12px)}}.nav{{min-height:66px;display:flex;align-items:center;justify-content:space-between;gap:24px}}.brand{{display:flex;align-items:center;gap:14px;text-decoration:none}}.brand img{{width:190px}}.brand span{{padding-left:14px;border-left:1px solid rgba(255,255,255,.18);color:var(--grey);font:10px ui-monospace,monospace;letter-spacing:.12em}}.links{{display:flex;gap:20px}}.links a{{color:var(--grey);font-size:12px;text-decoration:none}}.links a:hover,.links a[aria-current="page"]{{color:var(--white)}}
    .hero{{padding:72px 0;border-bottom:1px solid var(--line)}}.hero-grid{{display:grid;grid-template-columns:1fr minmax(380px,500px);gap:72px;align-items:center}}.eyebrow,.section-kicker{{margin:0 0 14px;color:var(--red);font:700 10px/1.2 ui-monospace,monospace;letter-spacing:.15em}}h1,h2,h3{{font-family:Jost,Arial,sans-serif}}h1{{margin:0;font-size:clamp(58px,9vw,104px);font-weight:600;line-height:.88;letter-spacing:-.055em}}.lead{{max-width:720px;margin:24px 0 0;color:var(--grey);font-size:17px}}.facts{{display:flex;flex-wrap:wrap;gap:8px;margin-top:28px}}.fact{{padding:7px 10px;border:1px solid rgba(255,255,255,.14);border-radius:8px;color:var(--grey);font-size:11px}}.icon-set{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding:14px;border:1px solid var(--line);border-radius:28px;background:var(--panel)}}.icon-set img{{width:100%;aspect-ratio:1;object-fit:contain;border-radius:50%;background:var(--panel-2)}}.icon-caption{{grid-column:1/-1;display:flex;justify-content:space-between;gap:12px;padding:4px 4px 0;color:var(--dim);font:10px ui-monospace,monospace}}
    .overview{{padding:64px 0;border-bottom:1px solid var(--line)}}.overview-head{{display:grid;grid-template-columns:100px 1fr;gap:18px;margin-bottom:28px}}.overview-head h2{{margin:0;font-size:clamp(38px,5vw,58px);line-height:1}}.overview-head p{{max-width:740px;margin:10px 0 0;color:var(--grey)}}.god-nav{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}.god-link{{display:flex;align-items:center;gap:14px;padding:12px;border:1px solid var(--line);border-radius:16px;background:var(--panel);text-decoration:none;transition:.18s ease}}.god-link:hover{{transform:translateY(-2px);border-color:var(--red)}}.god-icon{{flex:none;width:68px;height:68px;border-radius:50%;overflow:hidden;background:var(--panel-2)}}.god-icon img{{width:100%;height:100%;object-fit:contain}}.god-link strong{{display:block;font:600 21px/1.15 Jost,Arial,sans-serif}}.god-link small{{display:block;margin-top:4px;color:var(--grey);font-size:11px;line-height:1.35}}
    .deity{{padding:72px 0;border-bottom:1px solid var(--line);scroll-margin-top:66px}}.deity-head{{display:grid;grid-template-columns:150px minmax(0,780px);gap:28px;align-items:center;margin-bottom:34px}}.deity-icon{{width:150px;height:150px;border:1px solid var(--line);border-radius:50%;overflow:hidden;background:var(--panel)}}.deity-icon img{{width:100%;height:100%;object-fit:contain}}.deity-head h2{{margin:0;font-size:clamp(42px,6vw,68px);font-weight:600;line-height:.95;letter-spacing:-.035em}}.deity-head p{{max-width:760px;margin:14px 0 0;color:var(--grey);font-size:16px}}.attributes{{display:flex;flex-wrap:wrap;gap:7px;margin-top:16px}}.attributes span{{padding:6px 9px;border:1px solid rgba(255,255,255,.13);border-radius:7px;color:var(--grey);font-size:10px}}
    .grid{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}}.card{{min-width:0;padding:12px;border:1px solid var(--line);border-radius:15px;background:var(--panel)}}.stage{{min-height:190px;display:grid;place-items:center;overflow:hidden;border-radius:10px;background:var(--panel-2)}}.stage img{{width:min(95%,190px);height:184px;object-fit:contain}}.card-head{{display:grid;gap:3px;margin-top:12px}}.card h3{{margin:0;font-size:18px;font-weight:600;line-height:1.1}}.variant{{color:var(--red);font:700 9px ui-monospace,monospace;letter-spacing:.08em}}.card-note{{min-height:36px;margin:7px 0 0;color:var(--grey);font-size:11px}}.actions{{display:flex;flex-wrap:wrap;gap:5px;margin-top:10px}}.btn{{flex:none;padding:6px 7px;border:1px solid rgba(255,255,255,.18);border-radius:7px;text-decoration:none;font-size:9px;font-weight:700}}.btn:hover,.btn.primary{{border-color:var(--red)}}.source-file{{margin-top:10px;padding-top:8px;border-top:1px solid rgba(255,255,255,.07);color:var(--dim);font-size:9px}}.source-file summary{{cursor:pointer}}.source-file code{{display:block;margin-top:6px;overflow-wrap:anywhere}}
    .provenance{{padding:70px 0;border-bottom:1px solid var(--line)}}.specs{{margin:0;border:1px solid var(--line);border-radius:16px;overflow:hidden}}.spec{{display:grid;grid-template-columns:220px 1fr;gap:20px;padding:16px 19px;background:var(--panel);border-bottom:1px solid rgba(255,255,255,.08)}}.spec:last-child{{border-bottom:0}}.spec dt{{color:var(--grey)}}.spec dd{{margin:0}}.note{{margin-top:18px;padding:18px 20px;border-left:3px solid var(--red);border-radius:0 12px 12px 0;background:var(--panel);color:var(--grey);font-size:13px}}.note strong{{color:var(--white)}}footer{{padding:40px 0 60px;color:var(--dim);font-size:11px}}.footer{{display:flex;justify-content:space-between;gap:20px}}
    @media(max-width:1160px){{.grid{{grid-template-columns:repeat(4,minmax(0,1fr))}}.god-nav{{grid-template-columns:repeat(3,minmax(0,1fr))}}}}@media(max-width:940px){{.hero-grid{{grid-template-columns:1fr}}.icon-set{{max-width:500px}}.grid{{grid-template-columns:repeat(3,minmax(0,1fr))}}.god-nav{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}@media(max-width:720px){{.deity-head{{grid-template-columns:96px 1fr}}.deity-icon{{width:96px;height:96px}}.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}@media(max-width:560px){{.wrap{{width:min(calc(100% - 28px),var(--max))}}.links{{display:none}}.brand span{{display:none}}.hero,.overview,.deity,.provenance{{padding:50px 0}}.overview-head{{grid-template-columns:1fr;gap:8px}}.god-nav{{grid-template-columns:1fr}}.deity-head{{grid-template-columns:1fr;gap:18px}}.grid{{grid-template-columns:1fr}}.stage{{min-height:260px}}.stage img{{height:250px;width:min(95%,260px)}}.spec{{grid-template-columns:1fr;gap:4px}}.footer{{flex-direction:column}}}}
  </style>
</head>
<body>
  <nav aria-label="Разделы страницы"><div class="wrap nav"><a class="brand" href="index.html" aria-label="Вернуться в брендбук MOKO AI"><img src="assets/svg/logo/moko-ai-horus-horizontal-dark.svg" alt="MOKO AI"><span>ПАНТЕОН</span></a><div class="links"><a href="index.html">Брендбук</a><a href="#gods" aria-current="page">Боги</a><a href="#source">Источник</a></div><span class="mono" style="color:var(--dim);font-size:10px">12 БОГОВ · 120 ИКОНОК</span></div></nav>
  <main id="top">
    <header class="hero"><div class="wrap hero-grid"><div><p class="eyebrow">ЕГИПЕТСКИЙ ПАНТЕОН MOKO AI</p><h1>Боги<br>и символы</h1><p class="lead">Двенадцать узнаваемых образов египетского пантеона. У каждого бога — краткое описание, своя навигационная иконка и десять подготовленных вариантов.</p><div class="facts"><span class="fact">12 богов</span><span class="fact">120 готовых иконок</span><span class="fact">10 вариантов каждого образа</span><span class="fact">SVG · PNG · JPG · WebP</span></div></div><figure class="icon-set">{''.join(hero_icons)}<figcaption class="icon-caption"><span>НАВИГАЦИОННЫЙ НАБОР</span><span>12 СИМВОЛОВ</span></figcaption></figure></div></header>

    <section class="overview" id="gods"><div class="wrap"><div class="overview-head"><div class="section-kicker">ПУТЕВОДИТЕЛЬ</div><div><h2>Выберите бога</h2><p>Иконки ведут к описанию и десяти готовым вариантам каждого образа. Технические названия коллекций скрыты — в интерфейсе используются понятные русские обозначения.</p></div></div><div class="god-nav">
{chr(10).join(overview_cards)}
    </div></div></section>

{chr(10).join(sections)}

    <section class="provenance" id="source"><div class="wrap"><div class="overview-head"><div class="section-kicker">ИСТОЧНИК</div><div><h2>Полный подготовленный набор</h2><p>Все изображения опубликованы без перерисовки и изменения исходных SVG.</p></div></div><dl class="specs"><div class="spec"><dt>Источник</dt><dd>Google Drive · папка «ПАНТЕОН» · ID <code>1EDzc6O5Hoxfymjmn9axY5zs9vJ9nJRVg</code></dd></div><div class="spec"><dt>Состав</dt><dd>12 богов, по 10 вариантов для каждого: всего 120 SVG-файлов.</dd></div><div class="spec"><dt>Целостность</dt><dd>Исходные имена, каталоги и байты сохранены. Контрольные суммы записаны в <code>assets/svg/pantheon/manifest.csv</code>.</dd></div><div class="spec"><dt>Форматы</dt><dd>Каждый образ можно скачать как SVG, PNG, JPG или lossless WebP.</dd></div><div class="spec"><dt>Основной знак</dt><dd>Варианты Гора в Пантеоне не заменяют и не изменяют утверждённый логотип MOKO AI.</dd></div></dl><div class="note"><strong>Важно:</strong> на странице показаны только готовые файлы из пула владельца. Старые самостоятельно созданные варианты удалены.</div></div></section>
  </main>
  <footer><div class="wrap footer"><span>Пантеон MOKO AI · 12 богов · 120 подготовленных иконок · 2026-10-27</span><span><a href="index.html">Вернуться в брендбук</a></span></div></footer>
</body>
</html>
'''
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Built {OUTPUT.name}: {len(DEITIES)} gods, {len(all_files)} assets")


if __name__ == "__main__":
    main()
