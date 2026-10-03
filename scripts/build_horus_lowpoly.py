#!/usr/bin/env python3
"""Build the approved MOKO AI Horus SVG system.

The immutable geometry source is assets/svg/source/moko-ai-horus-reference.svg.
No raster reference is required. The bundled Jost variable font is used only to
convert AI to path outlines.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from textwrap import dedent

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "svg" / "source" / "moko-ai-horus-reference.svg"
LOGO_DIR = ROOT / "assets" / "svg" / "logo"
AVATAR_DIR = ROOT / "assets" / "svg" / "avatars"
NS = {"svg": "http://www.w3.org/2000/svg"}

MOKO_RED = "#d64545"
BLACK = "#050505"
LIGHT = "#f3f3f1"
WHITE = "#ffffff"
STATUS = {
    "online": "#4caf7d",
    "thinking": "#e0a33e",
    "action": "#4a7fb5",
}

RING_PATH = (
    "M 350 169.5 A 178 178 0 1 0 -6 169.5 "
    "A 178 178 0 1 0 350 169.5 Z "
    "M 342 169.5 A 170 170 0 1 1 2 169.5 "
    "A 170 170 0 1 1 342 169.5 Z"
)
COMPACT_RING_PATH = (
    "M 350 169.5 A 178 178 0 1 0 -6 169.5 "
    "A 178 178 0 1 0 350 169.5 Z "
    "M 336 169.5 A 164 164 0 1 1 8 169.5 "
    "A 164 164 0 1 1 336 169.5 Z"
)
AI_TRANSFORM = "translate(210 232) scale(0.081 -0.081)"


def load_reference() -> tuple[str, list[tuple[str, str]]]:
    root = ET.parse(SOURCE).getroot()
    clip_path = root.find(".//svg:clipPath/svg:path", NS)
    facets = root.find(".//svg:g[@id='contrast-facets']", NS)
    if clip_path is None or facets is None:
        raise RuntimeError(f"Invalid approved reference: {SOURCE}")
    polygons = [
        (polygon.attrib["points"], polygon.attrib["fill"].lower())
        for polygon in facets.findall("svg:polygon", NS)
    ]
    if len(polygons) != 24:
        raise RuntimeError(f"Approved reference must contain 24 facets, found {len(polygons)}")
    return clip_path.attrib["d"], polygons


SILHOUETTE_PATH, FACETS = load_reference()
FACET_COLORS = tuple(dict.fromkeys(fill for _, fill in FACETS))


def svg(title: str, description: str, body: str, view_box: str, width: int, height: int) -> str:
    return dedent(f'''\
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" width="{width}" height="{height}" role="img" aria-labelledby="title desc" shape-rendering="geometricPrecision">
      <title id="title">{title}</title>
      <desc id="desc">{description}</desc>
      <metadata>MOKO AI Horus identity; approved 2026-10-03; native SVG; version 2.0.0.</metadata>
    {body}
    </svg>
    ''')


def mark_fragment(prefix: str, *, colored: bool = True, color: str = MOKO_RED) -> str:
    if not colored:
        return f'  <path id="horus-silhouette-mark" d="{SILHOUETTE_PATH}" fill="{color}"/>'

    lines = [
        f'  <defs><clipPath id="{prefix}-silhouette" clipPathUnits="userSpaceOnUse"><path d="{SILHOUETTE_PATH}"/></clipPath></defs>',
        f'  <path id="{prefix}-silhouette-path" d="{SILHOUETTE_PATH}" fill="{MOKO_RED}"/>',
        f'  <g id="horus-lowpoly-mark" clip-path="url(#{prefix}-silhouette)" data-facets="24">',
    ]
    lines.extend(f'    <polygon points="{points}" fill="{fill}"/>' for points, fill in FACETS)
    lines.append("  </g>")
    return "\n".join(lines)


def ring(path: str = RING_PATH, color: str = MOKO_RED) -> str:
    return f'  <path id="moko-red-ring" d="{path}" fill="{color}" fill-rule="evenodd"/>'


def outlined_ai() -> str:
    font = TTFont(ROOT / "assets" / "fonts" / "jost" / "Jost-Variable.ttf")
    font = instantiateVariableFont(font, {"wght": 600}, inplace=False)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    metrics = font["hmtx"]
    output: list[str] = []
    x_position = 0
    for character in "AI":
        glyph_name = cmap[ord(character)]
        pen = SVGPathPen(glyph_set)
        glyph_set[glyph_name].draw(pen)
        output.append(f'    <path d="{pen.getCommands()}" transform="translate({x_position} 0)"/>')
        x_position += metrics[glyph_name][0]
    return "\n".join(output)


AI_PATHS = outlined_ai()


def ai_signature(color: str = MOKO_RED, transform: str = AI_TRANSFORM) -> str:
    return f'  <g id="ai-signature" transform="{transform}" fill="{color}" aria-label="AI">\n{AI_PATHS}\n  </g>'


def canvas(background: str) -> str:
    return f'  <rect x="-20" y="-22.5" width="384" height="384" fill="{background}"/>'


def circle_path(cx: float, cy: float, radius: float) -> str:
    return (
        f"M {cx + radius:g} {cy:g} A {radius:g} {radius:g} 0 1 0 {cx - radius:g} {cy:g} "
        f"A {radius:g} {radius:g} 0 1 0 {cx + radius:g} {cy:g} Z"
    )


def status_badge(color: str, background: str) -> str:
    return "\n".join([
        f'  <path d="{circle_path(322, 320, 25)}" fill="{background}"/>',
        f'  <path d="{circle_path(322, 320, 16)}" fill="{color}"/>',
    ])


def ring_composition(*, background: str | None = None, mono: bool = False, include_ai: bool = True, status: str | None = None) -> str:
    parts: list[str] = []
    if background:
        parts.append(canvas(background))
    if mono:
        parts.append(mark_fragment("mono", colored=False, color=WHITE))
        if include_ai:
            parts.append(ai_signature(WHITE))
        parts.append(ring(color=WHITE))
    else:
        parts.append(mark_fragment("avatar"))
        if include_ai:
            parts.append(ai_signature())
        parts.append(ring())
    if status:
        parts.append(status_badge(STATUS[status], background or BLACK))
    return "\n".join(parts)


def compact_avatar() -> str:
    return "\n".join([
        canvas(BLACK),
        mark_fragment("compact", colored=False, color=MOKO_RED),
        ring(COMPACT_RING_PATH),
    ])


def outlined_wordmark() -> str:
    tree = ET.parse(ROOT / "assets" / "svg" / "moko" / "logo-horizontal-white.svg")
    group = tree.getroot().find("svg:g[@id='word']", NS)
    if group is None:
        raise RuntimeError("Official MOKO wordmark group not found")
    return "\n".join(
        f'    <path d="{element.attrib["d"]}" fill="{{WORD}}" transform="{element.attrib["transform"]}"/>'
        for element in group
    )


def horizontal(theme: str) -> str:
    word_color = WHITE if theme == "dark" else BLACK
    mark = mark_fragment(f"horizontal-{theme}")
    body = f'''  <g transform="translate(-11 -11) scale(0.22)">
{mark}
  </g>
  <g transform="translate(-18 0)">
{outlined_wordmark().replace('{WORD}', word_color)}
  </g>
  <path d="M213 13H214V45H213Z" fill="#6b7177"/>
  <g transform="translate(222 44) scale(0.043 -0.043)" fill="{MOKO_RED}" aria-label="AI">
{AI_PATHS}
  </g>'''
    return svg(
        f'Горизонтальный логотип MOKO AI для {"тёмного" if theme == "dark" else "светлого"} фона',
        "Утверждённый знак Гора, официальный контурный wordmark MOKO и AI в контурах Jost SemiBold.",
        body,
        "0 0 272 58",
        272,
        58,
    )


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> None:
    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)

    write(LOGO_DIR / "moko-ai-horus-mark.svg", svg(
        "Эталонный знак MOKO AI в образе Гора",
        "Профиль сокола из 24 крупных контрастных low-poly граней на прозрачном фоне.",
        mark_fragment("mark"), "0 0 344 339", 344, 339,
    ))
    write(LOGO_DIR / "moko-ai-horus-mark-mono.svg", svg(
        "Монохромный знак MOKO AI",
        "Одноцветный белый силуэт утверждённого профиля Гора.",
        mark_fragment("mark-mono", colored=False, color=WHITE), "0 0 344 339", 344, 339,
    ))
    write(LOGO_DIR / "moko-ai-horus-ring.svg", svg(
        "Знак MOKO AI в красном кольце",
        "Эталонный профиль Гора из 24 граней в красном круговом кольце, без подписи AI.",
        ring_composition(include_ai=False), "-20 -22.5 384 384", 384, 384,
    ))
    write(LOGO_DIR / "moko-ai-horus-ring-ai.svg", svg(
        "Основная композиция MOKO AI",
        "Эталонный профиль Гора из 24 граней, красное кольцо и крупная подпись AI под клювом.",
        ring_composition(), "-20 -22.5 384 384", 384, 384,
    ))
    write(LOGO_DIR / "moko-ai-horus-horizontal-dark.svg", horizontal("dark"))
    write(LOGO_DIR / "moko-ai-horus-horizontal-light.svg", horizontal("light"))

    avatars = {
        "moko-ai-primary-dark.svg": svg(
            "Основной тёмный аватар MOKO AI", "Красное кольцо, профиль Гора и подпись AI на почти чёрном фоне.",
            ring_composition(background=BLACK), "-20 -22.5 384 384", 384, 384,
        ),
        "moko-ai-primary-light.svg": svg(
            "Основной светлый аватар MOKO AI", "Красное кольцо, профиль Гора и подпись AI на светлом фоне.",
            ring_composition(background=LIGHT), "-20 -22.5 384 384", 384, 384,
        ),
        "moko-ai-mono.svg": svg(
            "Монохромный аватар MOKO AI", "Белое кольцо, силуэт Гора и подпись AI на почти чёрном фоне.",
            ring_composition(background=BLACK, mono=True), "-20 -22.5 384 384", 384, 384,
        ),
        "moko-ai-small.svg": svg(
            "Компактный аватар MOKO AI", "Утолщённое красное кольцо и одноцветный силуэт Гора без подписи AI для 24–63 px.",
            compact_avatar(), "-20 -22.5 384 384", 384, 384,
        ),
        "moko-ai-transparent.svg": svg(
            "Прозрачный аватар MOKO AI", "Красное кольцо, профиль Гора и подпись AI на прозрачном фоне.",
            ring_composition(), "-20 -22.5 384 384", 384, 384,
        ),
        "moko-ai-online.svg": svg(
            "Аватар MOKO AI — доступен", "Основной тёмный аватар с зелёным индикатором доступности.",
            ring_composition(background=BLACK, status="online"), "-20 -22.5 384 384", 384, 384,
        ),
        "moko-ai-thinking.svg": svg(
            "Аватар MOKO AI — обработка", "Основной тёмный аватар с янтарным индикатором обработки.",
            ring_composition(background=BLACK, status="thinking"), "-20 -22.5 384 384", 384, 384,
        ),
        "moko-ai-action.svg": svg(
            "Аватар MOKO AI — выполнение", "Основной тёмный аватар с синим индикатором выполнения.",
            ring_composition(background=BLACK, status="action"), "-20 -22.5 384 384", 384, 384,
        ),
    }
    for filename, content in avatars.items():
        write(AVATAR_DIR / filename, content)

    print(
        f"Built approved MOKO AI system: {len(FACETS)} facets, "
        f"{len(FACET_COLORS)} facet colors, AI scale 180%"
    )


if __name__ == "__main__":
    main()
