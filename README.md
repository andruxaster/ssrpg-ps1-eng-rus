# Shinsetsu Samurai Spirits: Bushidou Retsuden — PS1 English / Russian

Фанатские переводы PS1-версии (SLPS-00814) и русский перевод версии Neo Geo CD, плюс весь инструментарий, которым они собраны.

*English summary: fan translations of the PS1 version (English dialogue port of MoriyaMug's NGCD translation + new translation of PS1-only lines; full Russian translation) and the Russian Neo Geo CD translation, with the complete Python toolchain used to build them. Ready-made xdelta patches are in `patches/`.*

## Готовые патчи (`patches/`)

| Папка | Что это | База | Результат (CRC32) |
|---|---|---|---|
| `ps1-ru/` | PS1, русский перевод, v12 | Redump PS1, single BIN, CRC32 `6A001A89` | `6457124C` |
| `ps1-en/` | PS1, английские диалоги, v2 | то же | `73768FCF` |
| `ngcd-ru/` | Neo Geo CD, русский перевод, v9 | японский образ или английский патч v1.10 (см. README_RU) | см. README_RU |

Накладывать xdelta3 (или DeltaPatcher), с `.cue` из той же папки:

```
xdelta3 -d -s "Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan).bin" \
   patches/ps1-ru/SSRPG_PS1_RU_v12.xdelta \
   "Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan) [RU].bin"
```

Подробности и история версий — в `README.txt` / `README_RU.txt` внутри каждой папки.

## Что переведено в PS1-версии (RU)

* Все диалоги: строки, совпадающие с NGCD, взяты из русского NGCD-перевода, строки, которые есть только на PS1, переведены отдельно (`ru_ps1/tr/`).
* Интерфейс, предметы, приёмы, бой, магазины, сундуки, сохранение, карта памяти, game over.
* Графика: иконки и подсветка команд в бою, таблички HP/SP/«ГНЕВ», цифры I–VI, главное меню, экран новой игры (профили, главы, режимы), вступительный текст, каллиграфия во вступительном ролике, названия мест.

## Устройство репозитория

| Путь | Содержимое |
|---|---|
| `tools/` | Общий инструментарий: разбор PS1-файлов (`ps1all`, `ps1msg`, `fld`), сопоставление с NGCD (`build_db`, `match`, `match2`), конвертация (`conv2`, `conv2ru`), шрифт из двухбуквенных глифов (`rupairs`, `rufont`, `encode`), сборка (`build`, `fldbuild`, `disc`), NGCD-инструменты (`ngdec`, `ngmsg`, `rubuild`, `uibuild`, `titleru`, `introru`…), дизассемблеры `mipsdis`/`m68dis`. Файлы `*_en.py` — варианты для английской сборки. |
| `tr/` | Английский перевод PS1-only реплик: `batch_*.json` (японский + контекст), `out_*.json` (перевод), глоссарий и инструкция. |
| `ru/tr/`, `ru/ui/`, `ru/tiles*.json` | Русский перевод NGCD-версии (диалоги, интерфейс, графические надписи) — база для русского PS1. |
| `ru_ps1/` | Русский PS1: `tools/pipeline.py` (диалоги → пары глифов), `tr/` (перевод PS1-only реплик). |
| `ps1ui/` | Интерфейс и графика PS1: инвентарь строк (`inventory.json`, `units.json`), переводы (`tr/`), `apply.py` (вшивает всё в образ), генераторы графики (`icons`, `plates`, `markers`, `pfxplates`, `pfxicons`, `callgfx`, `crawl`). |
| `mov/` | Каллиграфия во вступительном ролике (`OPEN_00.STR`) через jPSXdec. |
| `emu/` | Тестовый стенд: минимальный libretro-фронтенд `fe.c` (скрипт ввода на stdin, скриншоты, дампы RAM/VRAM, загрузка карты памяти `MCD=`), сценарии ввода, патч `pcsx_rearmed-vram.diff`. |
| `patches/` | Готовые патчи и README к ним. |

## Сборка

Нужны: Python 3 с `pillow numpy scipy capstone fonttools brotli`, `xdelta3`, `gcc`, Java + [jPSXdec](https://github.com/m35/jpsxdec) (только для ролика).

Данные игры и сторонние файлы в репозиторий не входят. Скрипты ищут их относительно корня (каталог с файлом `SSRPG_ROOT`) или `$SSRPG_WORK`:

```
ps1/fs/            распакованный PS1-образ (tools/bin2iso.py), ps1/*.bin — сам образ
ngcd/jp, ngcd/en   файлы NGCD-версии: японской и с английским патчем MoriyaMug v1.10
out/               промежуточные результаты (db.pkl, match.pkl, accepted.pkl, halves.pkl …)
fonts*/            шрифты (fontsource: Shantell Sans, Zen Antique, Press Start 2P, Tiny5 …; Mister Brush)
jpsx/              собранный jPSXdec
mov/w/fr/          кадры OPEN_00.STR, извлечённые jPSXdec (-vf png)
```

Вспомогательные программы: `gcc -O2 -o tools/eccfix tools/eccfix.c` (EDC/ECC), `gcc -O2 -o tools/iso2mode1 tools/iso2mode1.c`.

### Английская версия

```
python3 tools/build_db.py         # NGCD (jp+en) и PS1 → out/db.pkl
python3 tools/match.py && python3 tools/match2.py   # сопоставление реплик
python3 tools/export_tr.py        # батчи PS1-only реплик → tr/
python3 tools/runall.py           # тексты → out/converted.pkl, пары глифов
python3 tools/build_en.py && python3 tools/disc_en.py
```

### Русская версия

```
WITHUI=1 BUDGET=1540 python3 ru_ps1/tools/pipeline.py        # ~10 мин, → ru_ps1/out
python3 ps1ui/jpfree.py      # свободные слоты японского шрифта; 210 старших → ru_ps1/out/jp_free.json
python3 ps1ui/icons.py && python3 ps1ui/plates.py && python3 ps1ui/markers.py
python3 ps1ui/pfxplates.py && python3 ps1ui/pfxicons.py
PLATESZ=22 python3 ps1ui/callgfx.py
PS1OUT=ru_ps1/out PS1BUILD=build_ru RUFONT=1 python3 tools/build.py
python3 ps1ui/apply.py       # строго один раз после build.py
PS1BUILD=build_ru python3 tools/disc.py SSRPG_RU
sh mov/tools/apply_mov.sh build_ru/SSRPG_RU.bin
```

Сборка из этого репозитория проверена: результат совпадает с `patches/ps1-ru` байт в байт (CRC32 `6457124C`).

## Технические заметки

* Русский текст на PS1 выводится двухбуквенными глифами 16×16 на свободных SJIS-кодах: до 1360 штук в RAM с 0x801F2600 плюс 210 переиспользованных слотов японского шрифта. Хуки шрифта: 0x80023CC0 и 0x80029220.
* Наложения FIX-слоя в бою (FIX_00.PFX) собираются из тайлов 8×8 по 16 в ряду: рамка команды — 3×3 тайла (таблица в EXE по адресу 0x800CDC64), подсветка ячейки приёма — 2×2 (0x800CDD80).
* COMN.MSG: сообщения должны оставаться на исходных смещениях, управляющие коды пишутся в порядке байт `07 00`.
* Названия мест в списке сохранений берутся из блока типа 0x1a в каждой сцене полевых файлов и сохраняются внутри сейва.

## Авторы и благодарности

* Английский перевод NGCD-версии v1.10 — **MoriyaMug** (https://ko-fi.com/moriyamug); на нём построены английская PS1-версия и часть исходников русского перевода.
* Перевод, порт и инструменты — andruxaster при участии Claude (Anthropic).
* jPSXdec — m35; PCSX-ReARMed — libretro; шрифты — авторы Shantell Sans, Zen Antique, Press Start 2P, Tiny5, Mister Brush.

Shinsetsu Samurai Spirits: Bushidou Retsuden © 1997 SNK. Репозиторий не содержит файлов игры; для патчей нужен собственный образ.
