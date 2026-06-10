# Setup Guide

This guide walks you through getting the SuperWhisper Dashboard running on your machine.
**Estimated time: 5–10 minutes.**

---

## What you need

- [SuperWhisper](https://superwhisper.com) installed and with at least a few recordings
- Python 3.10 or newer ([python.org](https://python.org/downloads))
- A terminal (Terminal on macOS, PowerShell or CMD on Windows)

---

## Step 1 — Clone the repository

```bash
git clone https://github.com/Ihorbliz/superwhisper-dashboard.git
cd superwhisper-dashboard
```

---

## Step 2 — Check Python version

```bash
python --version    # needs 3.10 or newer
```

No external packages required — the dashboard uses only Python standard library.
If `python` is not found on macOS, use `python3` instead.

---

## Step 3 — Configure `config.py`  ← THE ONLY FILE YOU NEED TO EDIT

Open `config.py` in any text editor. There are **two things** to change:

### 3a. Set your recordings path

Find this block near the top of the file:

```python
# ★  CHANGE THIS  ★  CHANGE THIS  ★  CHANGE THIS  ★
RECORDINGS_PATH = "AUTO"
```

If `"AUTO"` works — great, you're done (the script tries to find SuperWhisper automatically).
If it doesn't, replace `"AUTO"` with the actual path:

**macOS:**
```python
RECORDINGS_PATH = "~/Library/Application Support/com.superwhisper.app/recordings"
```

**Windows:**
```python
RECORDINGS_PATH = "C:/Users/YOUR_USERNAME/AppData/Local/com.superwhisper.app/recordings"
```
> Replace `YOUR_USERNAME` with your actual Windows username (the folder name under `C:\Users\`)

**How to find it yourself:**
- macOS: open Finder → Go → Go to Folder → paste `~/Library/Application Support/com.superwhisper.app/recordings`
- Windows: open Explorer → paste `%LOCALAPPDATA%\com.superwhisper.app\recordings` in the address bar

---

### 3b. Set your typing speed

Find this block:

```python
# ★  CHANGE THIS  ★  Your personal typing speed
TYPING_SPEEDS = {
    'casual':       35,
    'professional': 44,   # ← THIS ONE is used in the dashboard — change it
    'fast':         60,
}
```

Change `44` to your own number: **your WPM × accuracy**.

**How to measure:**
1. Go to [monkeytype.com](https://monkeytype.com) or [keybr.com](https://keybr.com)
2. Run a 1-minute test
3. Multiply: e.g. `52 WPM × 0.91 accuracy = 47`
4. Put that number as `'professional'`

This is used to calculate how much time you saved by dictating instead of typing.
If you skip this step, the default `44` will be used.

---

### 3c. Set your meeting mode names (if needed)

By default the script treats any SuperWhisper mode whose name starts with `"meeting"` as a meeting recording (excluded from time-savings stats).

If you named your meeting modes differently — open `config.py` and update this line:

```python
MEETING_PREFIXES = ['meeting']  # add your own prefixes here
```

For example:
```python
MEETING_PREFIXES = ['meeting', 'нарада', 'call', 'zoom']
```

**How to find your mode names:** SuperWhisper → Settings → Modes → check the names of modes you use for recording meetings.

If all your meeting modes already start with `"meeting"` — skip this step.

---

## Step 4 — Verify the config

```bash
python config.py        # macOS/Linux: python3 config.py
```

You should see:
```
Recordings path OK: /path/to/your/recordings
Typing speed (professional): 44 WPM
```

---

## Step 5 — Sync your recordings

```bash
python sync_history.py        # macOS/Linux: python3 sync_history.py
```

Expected output:
```
Synced 143 new recordings. Total in history: 143
History saved to: /path/to/superwhisper-dashboard/history.json
```

Run this regularly — SuperWhisper deletes old recordings after ~1 month. Your `history.json` keeps them forever.

---

## Step 6 — Generate and open the dashboard

```bash
python generate_dashboard.py --lang en    # English
python generate_dashboard.py --lang ua    # Ukrainian
python generate_dashboard.py --lang both  # both at once
```

The dashboard opens automatically in your browser.

---

## One-click launchers (optional)

| Platform | File | What it does |
|----------|------|-------------|
| Windows | `SuperWhisper Stats UA.bat` | Sync + open Ukrainian dashboard |
| Windows | `SuperWhisper Stats EN.bat` | Sync + open English dashboard |
| macOS/Linux | `./run_ua.sh` | Sync + open Ukrainian dashboard |
| macOS/Linux | `./run_en.sh` | Sync + open English dashboard |

**macOS — make scripts executable first:**
```bash
chmod +x run_ua.sh run_en.sh sync_only.sh
```

---

## Automate sync (optional)

### Windows — Task Scheduler

```powershell
$path = (Get-Item .).FullName
schtasks /create /tn "SuperWhisper Sync" /tr "`"$path\sync_only.bat`"" /sc WEEKLY /d MON /st 10:00 /f
```

### macOS/Linux — cron

```bash
crontab -e
# Add this line (replace /full/path/to with the actual path):
0 10 * * 1 /full/path/to/superwhisper-dashboard/sync_only.sh >> /full/path/to/superwhisper-dashboard/sync_log.txt 2>&1
```

---

## Troubleshooting

| Problem | Solution |
|---------|---------|
| `Path not found` error | Check `RECORDINGS_PATH` in `config.py` |
| Dashboard is empty | Run `sync_history.py` first |
| `python` not found on macOS | Use `python3` instead |
| `.sh` script won't run | Run `chmod +x run_ua.sh` first |

---
---

# Інструкція з налаштування

Покроковий гайд для запуску SuperWhisper Dashboard на твоєму комп'ютері.
**Орієнтовний час: 5–10 хвилин.**

---

## Що потрібно

- [SuperWhisper](https://superwhisper.com) встановлений і є хоча б кілька записів
- Python 3.10 або новіший ([python.org](https://python.org/downloads))
- Термінал (Terminal на macOS, PowerShell або CMD на Windows)

---

## Крок 1 — Клонувати репозиторій

```bash
git clone https://github.com/Ihorbliz/superwhisper-dashboard.git
cd superwhisper-dashboard
```

---

## Крок 2 — Встановити залежності

```bash
pip install -r requirements.txt
```

## Крок 2 — Перевірити версію Python

```bash
python --version    # потрібна версія 3.10 або новіша
```

Зовнішні пакети не потрібні — дашборд використовує тільки стандартну бібліотеку Python.
Якщо `python` не знайдено на macOS — використовуй `python3`.

---

## Крок 3 — Налаштувати `config.py`  ← ЄДИНИЙ ФАЙЛ ЯКИЙ ТРЕБА ВІДРЕДАГУВАТИ

Відкрий `config.py` у будь-якому текстовому редакторі. Потрібно змінити **дві речі**:

### 3а. Вказати шлях до записів

Знайди цей блок на початку файлу:

```python
# ★  CHANGE THIS  ★  CHANGE THIS  ★  CHANGE THIS  ★
RECORDINGS_PATH = "AUTO"
```

Якщо `"AUTO"` спрацює — чудово, більше нічого міняти не треба (скрипт спробує знайти SuperWhisper автоматично).
Якщо ні — заміни `"AUTO"` на реальний шлях:

**macOS:**
```python
RECORDINGS_PATH = "~/Library/Application Support/com.superwhisper.app/recordings"
```

**Windows:**
```python
RECORDINGS_PATH = "C:/Users/ТВО_ІМ'Я/AppData/Local/com.superwhisper.app/recordings"
```
> Замість `ТВО_ІМ'Я` вкажи своє ім'я користувача Windows (назва папки в `C:\Users\`)

**Як знайти самостійно:**
- macOS: Finder → Перейти → Перейти до папки → вставити `~/Library/Application Support/com.superwhisper.app/recordings`
- Windows: Провідник → вставити `%LOCALAPPDATA%\com.superwhisper.app\recordings` в адресний рядок

---

### 3б. Вказати швидкість набору

Знайди цей блок:

```python
# ★  CHANGE THIS  ★  Your personal typing speed
TYPING_SPEEDS = {
    'casual':       35,
    'professional': 44,   # ← ЦЕ ЗНАЧЕННЯ використовується в дашборді — змінити
    'fast':         60,
}
```

Зміни `44` на своє число: **твій WPM × точність**.

**Як виміряти:**
1. Зайди на [monkeytype.com](https://monkeytype.com) або [keybr.com](https://keybr.com)
2. Пройди 1-хвилинний тест
3. Помнож: наприклад `52 WPM × 0.91 точність = 47`
4. Постав це число як `'professional'`

Якщо пропустити цей крок — буде використовуватись значення за замовчуванням `44`.

---

### 3в. Налаштувати назви режимів зустрічей (якщо потрібно)

За замовчуванням скрипт вважає зустріччю будь-який режим SuperWhisper, назва якого починається з `"meeting"`. Такі записи відстежуються окремо і не враховуються в розрахунку зекономленого часу.

Якщо твої режими для зустрічей названі інакше — відкрий `config.py` і оновити цей рядок:

```python
MEETING_PREFIXES = ['meeting']  # додай свої префікси сюди
```

Наприклад:
```python
MEETING_PREFIXES = ['meeting', 'нарада', 'call', 'zoom']
```

**Як знайти назви своїх режимів:** SuperWhisper → Налаштування → Режими → подивись назви режимів які використовуєш для запису зустрічей.

Якщо всі твої режими зустрічей вже починаються з `"meeting"` — цей крок можна пропустити.

---

## Крок 4 — Перевірити конфігурацію

```bash
python config.py        # macOS/Linux: python3 config.py
```

Маєш побачити:
```
Recordings path OK: /шлях/до/твоїх/записів
Typing speed (professional): 44 WPM
```

---

## Крок 5 — Синхронізувати записи

```bash
python sync_history.py        # macOS/Linux: python3 sync_history.py
```

Очікуваний результат:
```
Synced 143 new recordings. Total in history: 143
History saved to: /шлях/до/superwhisper-dashboard/history.json
```

Запускай регулярно — SuperWhisper видаляє старі записи через ~1 місяць. Твій `history.json` зберігає їх назавжди.

---

## Крок 6 — Згенерувати і відкрити дашборд

```bash
python generate_dashboard.py --lang ua    # Українська
python generate_dashboard.py --lang en    # Англійська
python generate_dashboard.py --lang both  # Обидві одразу
```

Дашборд відкриється автоматично в браузері.

---

## Лаунчери одним кліком (опційно)

| Платформа | Файл | Що робить |
|-----------|------|----------|
| Windows | `SuperWhisper Stats UA.bat` | Синхронізація + відкрити українську версію |
| Windows | `SuperWhisper Stats EN.bat` | Синхронізація + відкрити англійську версію |
| macOS/Linux | `./run_ua.sh` | Синхронізація + відкрити українську версію |
| macOS/Linux | `./run_en.sh` | Синхронізація + відкрити англійську версію |

**macOS — спочатку зробити скрипти виконуваними:**
```bash
chmod +x run_ua.sh run_en.sh sync_only.sh
```

---

## Автоматизація синхронізації (опційно)

### Windows — Планувальник завдань

```powershell
$path = (Get-Item .).FullName
schtasks /create /tn "SuperWhisper Sync" /tr "`"$path\sync_only.bat`"" /sc WEEKLY /d MON /st 10:00 /f
```

### macOS/Linux — cron

```bash
crontab -e
# Додати рядок (замінити /повний/шлях/до на реальний шлях):
0 10 * * 1 /повний/шлях/до/superwhisper-dashboard/sync_only.sh >> /повний/шлях/до/superwhisper-dashboard/sync_log.txt 2>&1
```

---

## Вирішення проблем

| Проблема | Рішення |
|----------|---------|
| Помилка `Path not found` | Перевір `RECORDINGS_PATH` у `config.py` |
| Дашборд порожній | Спочатку запусти `sync_history.py` |
| `python` не знайдено на macOS | Використовуй `python3` |
| `.sh` скрипт не запускається | Запусти `chmod +x run_ua.sh` |
