# Сборка APK «Solar» — пошагово

## Путь 0 (быстрый, без сборки): готовые APK
- **OllamaApp**: https://github.com/ollamaapp/ollama-android/releases → скачайте `app-release.apk`, ставьте на телефон, в настройках укажите URL Ollama `http://IP_ПК:11434`. Имя ассистента задаётся в настройках чата — напишите «Solar».
- **ChatterUI** (способ B, оффлайн): https://github.com/Vali-98/ChatterUI/releases → APK + инструкция по GGUF-моделям. Создайте персона с именем «Solar».

---

## Путь A: сборка Kivy-клиента (этот репозиторий) — Linux или Windows+WSL2

### 1. Инструменты на ПК
**Windows:**
```powershell
wsl --install -d Ubuntu-22.04
```
Откройте Ubuntu, далее — как на Linux.

**Linux (Ubuntu/Debian 22.04):**
```bash
sudo apt update && sudo apt install -y \
  openjdk-17-jdk git zip unzip autoconf libtool \
  pkg-config cmake ninja-build python3 python3-pip python3-venv \
  zlib1g-dev libncurses5-dev libffi-dev
```

### 2. Запуск сервера с моделью (на самом ПК, не в WSL!)
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh
OLLAMA_HOST=0.0.0.0:11434 ollama serve &
ollama pull qwen2.5:3b
sudo ufw allow 11434/tcp        # если включён файрвол

# Windows: установите OllamaSetup.exe с https://ollama.com/download
# затем в PowerShell:
setx OLLAMA_HOST "0.0.0.0:11434"   # после перезапуска приложения Ollama
```
Проверка с того же ПК: `curl http://localhost:11434/api/tags` → JSON со списком моделей.
Узнайте IP: Linux `hostname -I | awk '{print $1}'`, Windows `ipconfig` (IPv4).

⚠️ В WSL2 Ollama лучше запускать на Windows-стороне (или использовать `--network host` в новом WSL), иначе адрес будет `172.x.x.x` и телефон его не увидит.

### 3. Настройка клиента
В `solar_app/main.py` замените дефолт:
```python
DEFAULT_HOST = "http://192.168.1.100:11434"  # ваш IP из шага 2
```
(можно не менять — задать в приложении через «⚙ Настройки»).

### 4. Сборка APK
```bash
cd solar_app
python3 -m venv venv && source venv/bin/activate
pip install -U buildozer cython==0.29.36 kivy
buildozer android debug          # первый раз ~20-40 мин (скачает SDK/NDK)
# результат: bin/Solar-1.0-debug.apk
```
Релизная (подписанная) сборка:
```bash
buildozer android release
keytool -genkey -v -keystore solar.keystore -alias solar \
  -keyalg RSA -keysize 2048 -validity 10000
# apksigner из $ANDROID_HOME/build-tools/... подписывает автоматически при release
```

### 5. Переименование бота в «Solar» — где что находится
| Что | Где |
|---|---|
| Название на лаунчере | `buildozer.spec`: `title = Solar` |
| Имя в шапке чата | `main.py`: `BOT_NAME = "Solar"` |
| Характер/личность | `main.py`: `SYSTEM_PROMPT` |
| Package id | `buildozer.spec`: `package.name = solar`, `package.domain = org.solar` |

После изменения `title/package.*` делайте `buildozer android clean` перед пересборкой.

### 6. Установка на телефон
```bash
adb install -r bin/Solar-1.0-debug.apk
# или просто скопируйте APK на телефон и откройте (разрешите "неизвестные источники")
```
При первом запуске: ⚙ Настройки → введите `http://IP_ПК:11434` → модель `qwen2.5:3b` → Сохранить. Телефон и ПК — в одной Wi-Fi сети.

---

## Путь B: Flutter + llama.cpp (полностью автономный APK)

### 1. Инструменты
```bash
# Linux: скачайте SDK с https://docs.flutter.dev/get-started/install/linux
git clone https://github.com/flutter/flutter.git -b stable
export PATH=$PATH:$PWD/flutter/bin
flutter doctor    # поставьте отсутствующее: Android SDK, cmdline-tools, Java 17
flutter config --android-sdk ~/Android/Sdk
sdkmanager "platform-tools" "build-tools;34.0.0" "platforms;android-34"
```

### 2. Приложение
Готовые форки с llama.cpp:
- **ChatterUI** (рекомендуется): `git clone https://github.com/Vali-98/ChatterUI && cd ChatterUI`
- Или свой проект с плагином `llama_flutter_android` / `flutter_llama`:
```bash
flutter create solar_local
cd solar_local
flutter pub add flutter_llama   # bindings к llama.cpp через FFI
```

### 3. Модель GGUF
Скачайте квант ≤ размера RAM телефона минус 3–4 ГБ (для 8 ГБ RAM — модель 3–4B, Q4_K_M ≈ 2.3 ГБ):
```bash
# пример: Qwen2.5-3B-Instruct GGUF с HuggingFace
pip install "huggingface_hub[cli]"
hf download Qwen/Qwen2.5-3B-Instruct-GGUF qwen2.5-3b-instruct-q4_k_m.gguf --local-dir models/
```
В ChatterUI модели загружаются прямо в приложении (вкладка Models) — проще.

### 4. Имя «Solar» и сборка
- ChatterUI: создайте Character с Name=«Solar», System Prompt про Solar. Либо измените `lib/` дефолты.
```bash
flutter build apk --release --split-per-abi
# результат: build/app/outputs/flutter-apk/app-arm64-v8a-release.apk
flutter install   # установка подключённого телефона по adb
```

### 5. Типичные ошибки (Flutter/llama.cpp)
| Ошибка | Решение |
|---|---|
| `Unsupported class file major version` | Java ≠ 17: `sudo apt install openjdk-17-jdk && sudo update-alternatives --config java` |
| `licensing problem` NDK | Принять лицензии: `sdkmanager --licenses` |
| Crash при загрузке модели | Не хватило RAM → меньший квант (Q3/IQ3) или модель 1.5–3B |
| `Targeting S+ ... android:exported` | Обновите minSdk/pлагин, правьте AndroidManifest |
| Kivy: `Could not find a version that satisfies kivy` | `pip install "kivy[base] @ https://github.com/kivy/kivy/archive/master.zip"` или понизьте Cython до 0.29.36 |
| Buildozer: `SDK location not found` | `export ANDROID_SDK_ROOT=~/.buildozer/android/platform/android-sdk` |
| Buildozer завис на `Downloading android-ndk` | Проверьте диск (нужно 8–10 ГБ) и повторите; качается в `~/.buildozer` |
