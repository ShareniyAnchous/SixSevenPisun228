#!/usr/bin/env bash
# start_ollama.sh — запуск Ollama на ПК, доступного из локальной сети (способ A)
set -euo pipefail

# 1. Слушать все интерфейсы (иначе телефон не подключится)
export OLLAMA_HOST=0.0.0.0:11434

# 2. (Опционально)Models directory
# export OLLAMA_MODELS=/path/to/models

echo "== Запуск ollama serve =="
if ! command -v ollama >/dev/null; then
  echo "Ollama не установлен. Установка Linux:"
  echo "  curl -fsSL https://ollama.com/install.sh | sh"
  echo "Установка Windows: скачайте OllamaSetup.exe с https://ollama.com/download"
  exit 1
fi

# Небольшая модель, хорошо идущая по сети и на слабом железе:
ollama pull qwen2.5:3b || true

# Если systemd-сервис уже работает — перезапустим с новым окружением,
# иначе запускаем в foreground:
if systemctl is-active --quiet ollama 2>/dev/null; then
  sudo systemctl edit ollama.service <<'EOF' || true
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF
  sudo systemctl daemon-reload && sudo systemctl restart ollama
  echo "Сервис перезапущен. Логи: journalctl -u ollama -f"
else
  exec ollama serve
fi
