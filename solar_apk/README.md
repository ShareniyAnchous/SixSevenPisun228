# Solar — ИИ-бот для Android (.apk)

## Варианты решений (A — клиент к Ollama на ПК, B — локальная модель в телефоне)

| # | Проект | GitHub | Что умеет | APK | Локальные модели |
|---|--------|--------|-----------|-----|------------------|
| 1 | **OllamaApp** | https://github.com/ollamaapp/ollama-android | Чат с ANY OpenAI-совместимым API: Ollama, LM Studio, llama.cpp server, OpenRouter | Готовый APK в Releases + исходники Flutter (`flutter build apk`) | ✅ Да (через сервер Ollama/llama.cpp по сети) |
| 2 | **ChatterUI** | https://github.com/Vali-98/ChatterUI | Оффлайн-чат на llama.cpp прямо на телефоне + режим удалённого API. GGUF-конвертеры, настройки контекста | Готовый APK в Releases; пересборка из Flutter | ✅ Да (llama.cpp in-app, .gguf модели) |
| 3 | **Maid** | https://github.com/MobileLLM/Maid | Полностью оффлайн ассистент (llama.cpp), загрузка моделей с HuggingFace | Готовый APK в Releases | ✅ Да |
| 4 | **Solar-kivy (здесь)** | папка `solar_apk/solar_app` | Минимальный чат-клиент Python+Kivy → HTTP к Ollama на вашем ПК. Имя «Solar» из коробки | Сборка Buildozer (Linux/WSL2) | ✅ Клиент способа A |

**Рекомендация:** способ A = **OllamaApp** (или готовый Kivy-клиент здесь для полного контроля). Способ B = **ChatterUI**.

## Структура
- `solar_app/` — проект Kivy (main.py, ollama_client.py, buildozer.spec)
- `server/` — скрипты запуска Ollama на ПК + CORS-прокси
- `docs/BUILD.md` — пошаговая инструкция сборки APK (Windows WSL2 / Linux)
- `docs/PITFALLS.md` — подводные камни (RAM, нагрев, размер APK)
- `CHECKLIST.md` — чек-лист по этапам

## Быстрый старт (способ A)
1. На ПК: `ollama serve`, затем `ollama pull qwen2.5:3b` (или `llama3.2:3b`).
2. Узнать IP ПК: Linux/macOS `hostname -I`, Windows `ipconfig` (IPv4).
3. Открыть порт: `sudo ufw allow 11434/tcp` (Linux) или правило брандмауэра Windows.
4. Установить APK на телефон (тот же Wi-Fi!), указать `http://IP_ПК:11434`.
5. Имя бота «Solar», системный промпт уже задан в коде.
