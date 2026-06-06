# 🎵 Discord Music Bot

Музичний та утилітарний бот для Discord.

Підтримує:
- ▶️ Відтворення музики з YouTube
- ⏸️ Пауза / Резюм / Скіп
- 🔁 Плейлісти(черга відтворення)
- 🎲 Випадкові або вибіркові mp3 з локальної папки `bar/`
- 👋 Вітання нових учасників + ролі
- 💬 Монетка, питання до Лівсі(чатбот), адмін-команди

---

## 📌 Вимоги

- Python 3.11 (обов'язково)
- FFmpeg
- Discord Bot Token
- Windows / Linux / macOS

---

## 🚀 Запуск (Windows)

1. Встановіть **Python 3.11+**
2. Встановіть FFmpeg і додайте його в PATH
3. Склонуйте репозиторій
4. Перейменуйте config(example).py у config.py
5. У файлі config.py вставте токен свого боту і відповідні значення в інші змінні за бажанням
6. Запустіть `run.bat`

Бот сам:
- створить venv
- встановить залежності
- запуститься

## ⚙️ Встановлення та налаштування для Linux/MacOS

```bash
git clone https://github.com/Angrenlass/Doctor-Livesey.git
cd Doctor-Livesey

Python та віртуальне середовище:
Переконайся, що встановлений Python 3.11
python --version
За потреби поміняй python interpreter в IDE
У VScode - ctrl + shit + P
і шукай Python: Select Iterpreter

Створи та активуй venv:
python -m venv venv
для Linux/MacOS:
source venv/bin/activate

Встановлення залежностей:
pip install -r requirements.txt
завантажити FFmpeg(https://ffmpeg.org/download.html)

Перевірити:
ffmpeg -version

!)вказати шлях у коді у music.py, якщо Linux/MacOS:
ytdl_format_options = {
    ...
    'ffmpeg_location': r'шлях', 
}

Конфігурація:
Перейменувати config(example).py у config.py
У файлі config.py вставити токен свого боту і відповідні значення в інші змінні за бажанням

Запуск бота:
py main.py
Якщо все ок — побачиш:
Bot connected
```
## Ліцензія:
MIT / для особистого використання
