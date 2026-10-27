# MOKO AI Brandbook

Версия 2.3.1 · SVG-first

Брендбук ИИ-аккаунта MOKO AI на основе фирменной системы [MOKO Systems](https://moko.by/brandbook/). Полный подготовленный владельцем пул египетского Пантеона опубликован на отдельной странице `pantheon.html`.

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

## Пантеон

Отдельная страница содержит **все 120 подготовленных SVG** из папки владельца `ПАНТЕОН` на Google Drive. Исходные файлы опубликованы без перерисовки, отбора, переименования или изменения байтов.

- страница: [`pantheon.html`](pantheon.html);
- полный пул: `assets/svg/pantheon/`;
- 12 богов, по 10 вариантов каждого; навигационный набор из 12 иконок;
- человекочитаемые русские названия и краткое описание каждого бога;
- в источнике сохранены 10 каталогов, 120 SVG и 1 787 320 байт;
- контрольные суммы: `assets/svg/pantheon/manifest.csv`;
- проверка целостности: `assets/svg/pantheon/verify_snapshot.py`;
- генератор страницы: `scripts/build_pantheon_gallery.py` — он перечисляет файлы, но не изменяет изображения;
- для каждого SVG доступны PNG, JPG и lossless WebP;
- коллекция не заменяет и не изменяет утверждённый знак Гора.

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
    ├── pantheon/           # 120 SVG из подготовленного пула владельца
    └── source/             # утверждённый эталон формы

exports/
├── png/                    # прозрачные PNG для скачивания
├── jpg/                    # JPG на светлом или тёмном фоне
└── webp/                   # lossless WebP с прозрачностью

docs/
├── CREATIVE-LOG.md         # журнал креативов
├── CREATIVE-MEMORY.md      # актуальный контекст
├── DECISIONS.md            # решения
└── SOURCES.md              # источники
```

## Сборка и проверка

```bash
python3 scripts/build_horus_lowpoly.py
python3 scripts/build_pantheon_gallery.py
python3 assets/svg/pantheon/verify_snapshot.py
python3 scripts/export_rasters.py
python3 scripts/validate_svgs.py
```

Генератор Гора читает только утверждённый SVG-эталон. Генератор галереи не создаёт и не изменяет изображения: он строит страницу из готового пула владельца.

Для каждого SVG опубликованы загрузки в PNG, JPG и WebP:

- `exports/png/` — прозрачные PNG;
- `exports/jpg/` — JPG на светлом или тёмном фоне;
- `exports/webp/` — lossless WebP с прозрачностью;
- SVG остаётся мастер-форматом.

## Ссылки

- Брендбук: https://mokoaibot.github.io/moko-ai-brand-book/
- Пантеон: https://mokoaibot.github.io/moko-ai-brand-book/pantheon.html
- Репозиторий: https://github.com/mokoaibot/moko-ai-brand-book
