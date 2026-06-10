# SuperWhisper Dashboard

An interactive analytics dashboard for [SuperWhisper](https://superwhisper.com) — the AI voice dictation app for Mac.

Turns your voice recording history into a beautiful, animated HTML dashboard with period switching (Day / Week / Month / Year / All time), time-savings calculations, and charts. Works fully offline — no server, no cloud, just a Python script and a local HTML file.

Available in **Ukrainian** and **English**.

---

## Why this exists

SuperWhisper deletes recordings after approximately one month. If you use it daily, you lose your history — and any ability to see how your usage evolves over time.

This project solves three problems:

1. **History loss** — `sync_history.py` reads your recordings before they're deleted and saves them permanently to `history.json`. Run it weekly and you never lose data.

2. **No built-in stats** — SuperWhisper has no analytics. This dashboard shows you how many words you've dictated, how fast you speak, how much time you saved vs typing, and when you're most active.

3. **Meaningful metric** — the "time saved" card answers the question: *how much faster is voice than typing, for me personally?* It uses your actual typing speed, not a generic default.

---

## What the dashboard shows

### Period tabs — Day / Week / Month / Year / All time

Every stat card and number updates instantly when you switch periods. The charts always show the last 60 days.

### Stat cards

| Card | What it shows |
|------|--------------|
| **Time saved** | Minutes or hours you saved by speaking instead of typing, for the selected period |
| **Words dictated** | Total word count + average speaking speed (WPM) |
| **Meetings** | Count of meeting recordings — tracked separately, excluded from savings |
| **Dictation hours** | Total time you spent dictating in the period |

### Charts

**Activity over 60 days** — stacked bar chart showing dictation minutes (blue) and meeting minutes (orange) per day. Lets you see your usage patterns and quiet periods at a glance.

**Time saved per day** — area line chart with a hover tooltip. Mouse over any point to see the exact minutes (or hours) saved that day. The tooltip shows the value in the most readable unit: minutes below 60, hours above.

**Activity by hour** — bar chart showing which hours of the day you dictate the most. Useful for understanding your personal rhythm.

**Overall statistics** — four mini-cards showing all-time totals: dictation hours, meeting hours, total recordings, and average speaking speed.

---

## How the time savings formula works

```
saved_minutes = (word_count / typing_wpm) - recording_minutes
```

In plain language: if you dictated 200 words in 1.5 minutes, and your typing speed is 44 WPM, you would have needed 200 ÷ 44 = 4.5 minutes to type the same text. You saved 4.5 − 1.5 = **3 minutes**.

`typing_wpm` is your personal value from `config.py` — set it to `raw_speed × accuracy`. A typical value for someone who types reasonably well in their native language is 40–60 WPM.

If `saved_minutes` is negative (you typed faster than you spoke), the value is clamped to zero.

---

## Why meetings are excluded

Recordings where the SuperWhisper mode name starts with `"Meeting"` (e.g. `"Meeting OPUS"`, `"Meeting Whisper"`) are tracked in a separate card and excluded from time-savings calculations.

The reasoning: during a meeting you're not choosing between voice and keyboard — you're just recording what's being said. Counting meeting recordings as "time saved" would inflate the metric with something that doesn't represent a real efficiency gain.

Meeting minutes still appear in the activity chart (orange bars) so you can see your total recording volume.

### Custom meeting mode names

By default the script treats any mode whose name **starts with** `"meeting"` (case-insensitive) as a meeting. If you named your meeting modes differently in SuperWhisper — for example `"Нарада"`, `"Call"`, or `"Zoom"` — you need to update `MEETING_PREFIXES` in `config.py`:

```python
# config.py
MEETING_PREFIXES = ['meeting']           # default
MEETING_PREFIXES = ['meeting', 'нарада', 'call']   # example with custom names
```

How to check what your modes are called: open SuperWhisper → Settings → Modes → look at the names you use for meeting recording. Add any of them (or just the beginning of the name) to the list.

---

## Architecture

```
SuperWhisper app
  └── recordings/
        └── {folder_id}/
              └── meta.json   ← one file per recording
                                 contains: datetime, duration, modeName,
                                           result (transcript), modelName

          ↓  sync_history.py (run weekly)

      history.json            ← permanent archive, gitignored
                                 deduplicates by folder ID
                                 survives SuperWhisper's auto-delete

          ↓  generate_dashboard.py --lang ua/en/both

      dashboard_ua.html       ← self-contained HTML, no server needed
      dashboard_en.html       ← opens directly in any browser
```

### `sync_history.py`

- Reads every `meta.json` in your SuperWhisper recordings folder
- Extracts: datetime, duration, mode name, transcript length, word count, model, app version
- Detects recording type: `'meeting'` if `modeName.lower().startswith('meeting')`, else `'dictation'`
- Appends only **new** records to `history.json` (deduplication by folder name — safe to run multiple times)
- Updates `last_sync` timestamp

### `generate_dashboard.py`

- Reads `history.json`
- Computes per-period stats (day/week/month/year/all) for all cards
- Builds 60-day chart data and 24-hour activity data
- Generates a complete self-contained HTML file with all data embedded as JavaScript constants
- Supports `--lang ua` (Ukrainian), `--lang en` (English), or `--lang both`
- Opens the dashboard automatically after generation

### `config.py`

- `RECORDINGS_PATH` — where your SuperWhisper recordings live. Set to `"AUTO"` for auto-detection, or set the path manually.
- `TYPING_SPEEDS['professional']` — your personal WPM × accuracy, used in the time savings calculation

---

## File reference

| File | Purpose | Edit? |
|------|---------|-------|
| `config.py` | Your path + typing speed | **Yes — required** |
| `sync_history.py` | Reads recordings, builds history.json | No |
| `generate_dashboard.py` | Builds dashboard HTML from history.json | No |
| `history.json` | Your personal recording archive | No (auto-generated) |
| `dashboard_ua.html` | Ukrainian dashboard | No (auto-generated) |
| `dashboard_en.html` | English dashboard | No (auto-generated) |
| `SuperWhisper Stats UA.bat` | Windows launcher — Ukrainian | No |
| `SuperWhisper Stats EN.bat` | Windows launcher — English | No |
| `run_ua.sh` | macOS/Linux launcher — Ukrainian | No |
| `run_en.sh` | macOS/Linux launcher — English | No |
| `sync_only.bat` / `sync_only.sh` | Sync without opening browser — for schedulers | No |

---

## Quick start

```bash
git clone https://github.com/Ihorbliz/superwhisper-dashboard.git
cd superwhisper-dashboard

# Edit config.py — set RECORDINGS_PATH, TYPING_WPM, and MEETING_PREFIXES if needed

python sync_history.py
python generate_dashboard.py --lang en
```

No external dependencies — only Python 3.10+ standard library is required.

See [SETUP.md](SETUP.md) for the full step-by-step guide including automation and troubleshooting.

---

## Based on

This project was inspired by and built on top of [crarau/superwhisper-analysis](https://github.com/crarau/superwhisper-analysis) by [@crarau](https://github.com/crarau) — the original SuperWhisper data analysis toolkit.

The original project introduced the approach of reading SuperWhisper's `meta.json` files and the `config.py` structure that we adopted and extended. We built on that foundation to add: permanent history storage (so data survives SuperWhisper's auto-delete), an interactive HTML dashboard with period switching and animated charts, bilingual support (Ukrainian / English), meeting detection and exclusion from savings calculations, and one-click launchers for Windows and macOS.

---

Built with [Claude](https://claude.ai) + [SuperWhisper](https://superwhisper.com).

---
---

# SuperWhisper Dashboard

Інтерактивний аналітичний дашборд для [SuperWhisper](https://superwhisper.com) — AI-застосунку для голосової диктовки на Mac.

Перетворює історію голосових записів на красивий анімований HTML-дашборд з перемиканням періодів (День / Тиждень / Місяць / Рік / Весь час), розрахунком зекономленого часу та графіками. Працює повністю офлайн — без сервера, без хмари, тільки Python-скрипт і локальний HTML-файл.

Доступний **українською** та **англійською** мовами.

---

## Навіщо це зроблено

SuperWhisper видаляє записи приблизно через місяць. Якщо користуватись ним щодня — втрачається вся історія і будь-яка можливість бачити як змінюється використання з часом.

Цей проект вирішує три проблеми:

1. **Втрата історії** — `sync_history.py` зчитує записи до того як SuperWhisper їх видалить і зберігає назавжди в `history.json`. Запускай раз на тиждень — дані не зникнуть ніколи.

2. **Відсутність статистики** — у SuperWhisper немає аналітики. Цей дашборд показує скільки слів надиктовано, з якою швидкістю говориш, скільки часу заощаджено порівняно з набором тексту та коли ти найактивніший.

3. **Персональна метрика** — картка «зекономлений час» відповідає на питання: *наскільки голос швидший за клавіатуру саме для мене?* Використовується твоя реальна швидкість набору, а не якийсь загальний показник.

---

## Що показує дашборд

### Вкладки періодів — День / Тиждень / Місяць / Рік / Весь час

Всі картки оновлюються миттєво при перемиканні. Графіки завжди показують останні 60 днів.

### Картки статистики

| Картка | Що показує |
|--------|-----------|
| **Зекономлено часу** | Хвилини або години, заощаджені завдяки голосу замість набору, за обраний період |
| **Слів надиктовано** | Загальна кількість слів + середня швидкість мовлення (WPM) |
| **Зустрічі** | Кількість записів зустрічей — відстежуються окремо, не враховуються в економії |
| **Години диктовки** | Загальний час диктовки за обраний період |

### Графіки

**Активність за 60 днів** — стовпчастий графік з хвилинами диктовки (синій) та зустрічей (помаранчевий) по днях. Дозволяє бачити патерни використання.

**Зекономлений час по днях** — лінійний графік із підказкою при наведенні. Наведи на будь-яку точку — побачиш точну кількість хвилин або годин, зекономлених того дня.

**Активність по годинах** — стовпчастий графік, який показує в які години дня ти диктуєш найбільше.

**Загальна статистика** — чотири міні-картки з підсумками за весь час: години диктовки, години зустрічей, всього записів, середня швидкість мовлення.

---

## Як працює формула зекономленого часу

```
зекономлено_хвилин = (кількість_слів / швидкість_набору_wpm) - тривалість_запису_хв
```

Простими словами: якщо надиктовано 200 слів за 1.5 хвилини, а швидкість набору 44 WPM — тоді набір зайняв би 200 ÷ 44 = 4.5 хвилини. Заощаджено 4.5 − 1.5 = **3 хвилини**.

`швидкість_набору_wpm` — це твоє особисте значення з `config.py`: `сирий_WPM × точність`. Типове значення для людини яка нормально друкує рідною мовою — 40–60 WPM.

Якщо значення від'ємне (набирав би швидше ніж говорив) — воно обрізається до нуля.

---

## Чому зустрічі виключені

Записи, де назва режиму SuperWhisper починається з `"Meeting"` (наприклад `"Meeting OPUS"`, `"Meeting Whisper"`), відстежуються в окремій картці і не враховуються в розрахунку зекономленого часу.

Логіка така: під час зустрічі не обираєш між голосом і клавіатурою — просто записуєш що говорять. Рахувати це як «заощаджений час» означало б завищувати метрику тим що не є реальним виграшем в ефективності.

Хвилини зустрічей все одно відображаються на графіку активності (помаранчеві стовпці) — щоб бачити загальний обсяг записів.

### Кастомні назви режимів зустрічей

За замовчуванням скрипт вважає зустріччю будь-який режим, назва якого **починається** з `"meeting"` (без урахування регістру). Якщо у тебе режими для зустрічей названі інакше — наприклад `"Нарада"`, `"Call"` або `"Zoom"` — потрібно оновити `MEETING_PREFIXES` у `config.py`:

```python
# config.py
MEETING_PREFIXES = ['meeting']                      # за замовчуванням
MEETING_PREFIXES = ['meeting', 'нарада', 'call']    # приклад з кастомними назвами
```

Як перевірити назви своїх режимів: відкрий SuperWhisper → Налаштування → Режими → подивись як називаються режими для запису зустрічей. Додай їх (або початок назви) у список.

---

## Архітектура

```
SuperWhisper app
  └── recordings/
        └── {folder_id}/
              └── meta.json   ← один файл на запис
                                 містить: datetime, duration, modeName,
                                          result (транскрипт), modelName

          ↓  sync_history.py (запускати щотижня)

      history.json            ← постійний архів, у .gitignore
                                 дедублікація за ID папки
                                 переживає автовидалення SuperWhisper

          ↓  generate_dashboard.py --lang ua/en/both

      dashboard_ua.html       ← самодостатній HTML, сервер не потрібен
      dashboard_en.html       ← відкривається в будь-якому браузері
```

### `sync_history.py`

- Читає кожен `meta.json` у папці записів SuperWhisper
- Витягує: дату/час, тривалість, назву режиму, довжину транскрипту, кількість слів, модель, версію застосунку
- Визначає тип запису: `'meeting'` якщо `modeName.lower().startswith('meeting')`, інакше `'dictation'`
- Додає тільки **нові** записи до `history.json` (дедублікація за назвою папки — безпечно запускати кілька разів)
- Оновлює мітку часу `last_sync`

### `generate_dashboard.py`

- Читає `history.json`
- Обчислює статистику по кожному періоду (день/тиждень/місяць/рік/весь час)
- Будує дані для графіка за 60 днів і активності по годинах
- Генерує повний самодостатній HTML-файл з усіма даними вбудованими як JS-константи
- Підтримує `--lang ua` (українська), `--lang en` (англійська), або `--lang both`
- Автоматично відкриває дашборд після генерації

### `config.py`

- `RECORDINGS_PATH` — де знаходяться твої записи SuperWhisper. Встанови `"AUTO"` для автодетекту або вкажи шлях вручну.
- `TYPING_SPEEDS['professional']` — твій особистий WPM × точність, використовується у формулі економії часу

---

## Довідник файлів

| Файл | Призначення | Редагувати? |
|------|-------------|-------------|
| `config.py` | Твій шлях + швидкість набору | **Так — обов'язково** |
| `sync_history.py` | Зчитує записи, будує history.json | Ні |
| `generate_dashboard.py` | Будує HTML-дашборд з history.json | Ні |
| `history.json` | Особистий архів записів | Ні (генерується автоматично) |
| `dashboard_ua.html` | Украномовний дашборд | Ні (генерується автоматично) |
| `dashboard_en.html` | Англомовний дашборд | Ні (генерується автоматично) |
| `SuperWhisper Stats UA.bat` | Лаунчер Windows — українська | Ні |
| `SuperWhisper Stats EN.bat` | Лаунчер Windows — англійська | Ні |
| `run_ua.sh` | Лаунчер macOS/Linux — українська | Ні |
| `run_en.sh` | Лаунчер macOS/Linux — англійська | Ні |
| `sync_only.bat` / `sync_only.sh` | Тільки синхронізація — для планувальника | Ні |

---

## Швидкий старт

```bash
git clone https://github.com/Ihorbliz/superwhisper-dashboard.git
cd superwhisper-dashboard

# Відредагуй config.py — встанови RECORDINGS_PATH, TYPING_WPM і MEETING_PREFIXES якщо потрібно

python sync_history.py
python generate_dashboard.py --lang ua
```

Зовнішні залежності не потрібні — тільки стандартна бібліотека Python 3.10+.

Повна покрокова інструкція — у [SETUP.md](SETUP.md).

---

## На основі

Цей проект натхненний і побудований на основі [crarau/superwhisper-analysis](https://github.com/crarau/superwhisper-analysis) від [@crarau](https://github.com/crarau) — оригінального інструменту аналізу даних SuperWhisper.

Оригінальний проект запропонував підхід до читання `meta.json` файлів SuperWhisper і структуру `config.py`, яку ми прийняли і розширили. На цій основі ми додали: постійне збереження історії (дані не зникають після автовидалення SuperWhisper), інтерактивний HTML-дашборд з перемиканням періодів і анімованими графіками, двомовну підтримку (українська / англійська), визначення та виключення зустрічей з розрахунку економії, і лаунчери для Windows та macOS.

---

Зроблено з [Claude](https://claude.ai) + [SuperWhisper](https://superwhisper.com).
