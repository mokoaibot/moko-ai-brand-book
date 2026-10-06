# MOKO AI Brandbook

Версия 2.0.0 · SVG-first

Брендбук ИИ-аккаунта MOKO AI на основе фирменной системы [MOKO Systems](https://moko.by/brandbook/).

![Основной аватар MOKO AI](assets/svg/avatars/moko-ai-primary-dark.svg)

## Утверждённая система

- профиль сокола — образ бога Гора;
- 24 крупные контрастные low-poly грани;
- гладкий контур из кубических кривых Безье;
- красное круговое кольцо;
- `AI` в Jost SemiBold, размер 180%, переведено в контуры;
- градиенты и растровые вставки отсутствуют.

## Основные файлы

| Файл | Назначение |
|---|---|
| [`moko-ai-horus-reference.svg`](assets/svg/source/moko-ai-horus-reference.svg) | неизменяемый эталон формы |
| [`moko-ai-horus-mark.svg`](assets/svg/logo/moko-ai-horus-mark.svg) | знак без кольца |
| [`moko-ai-horus-ring.svg`](assets/svg/logo/moko-ai-horus-ring.svg) | знак в красном кольце |
| [`moko-ai-horus-ring-ai.svg`](assets/svg/logo/moko-ai-horus-ring-ai.svg) | основная прозрачная композиция |
| [`moko-ai-primary-dark.svg`](assets/svg/avatars/moko-ai-primary-dark.svg) | основной аватар |
| [`moko-ai-small.svg`](assets/svg/avatars/moko-ai-small.svg) | компактный аватар 24–63 px |

## Шрифты

- `MOKO` — официальный wordmark Century Gothic в кривых.
- `AI` и заголовки — Jost.
- Основной текст — Inter.
- Jost и Inter хранятся локально в `assets/fonts/` под OFL-1.1.

## Структура

```text
assets/
├── fonts/                  # Jost, Inter и лицензии
└── svg/
    ├── avatars/            # аватары и состояния
    ├── logo/               # знак и логотипы MOKO AI
    ├── moko/               # официальные исходники MOKO
    └── source/             # утверждённый эталон формы

exports/
├── png/                    # прозрачные PNG для скачивания
└── jpg/                    # JPG на светлом или тёмном фоне

docs/
├── CREATIVE-LOG.md         # журнал креативов
├── CREATIVE-MEMORY.md      # актуальный контекст
├── DECISIONS.md            # решения
└── SOURCES.md              # источники
```

## Сборка и проверка

```bash
python3 scripts/build_horus_lowpoly.py
python3 scripts/export_rasters.py
python3 scripts/validate_svgs.py
```

Генератор не использует растровый референс: форма читается из утверждённого SVG-эталона.

Для каждого SVG опубликованы загрузки в PNG и JPG:

- `exports/png/` — прозрачные PNG;
- `exports/jpg/` — JPG на светлом или тёмном фоне;
- SVG остаётся мастер-форматом.

## Ссылки

- Брендбук: https://mokoaibot.github.io/moko-ai-brand-book/
- Репозиторий: https://github.com/mokoaibot/moko-ai-brand-book
