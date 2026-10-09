"""HTTP-клиент для Ollama (/api/chat). Только stdlib — совместимо с python-for-android."""
import json
import urllib.error
import urllib.request


class OllamaError(Exception):
    pass


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def chat(self, messages):
        """messages: [{'role': 'system|user|assistant', 'content': str}, ...]
        Возвращает строку-ответ. Не-стриминг (проще и надёжнее для P4A)."""
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.7, "num_ctx": 4096},
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.URLError as e:
            raise OllamaError(
                f"Сервер недоступен ({self.base_url}). Проверьте: тот ли Wi-Fi, "
                f"запущен ли 'ollama serve', открыт ли порт 11434. Детали: {e.reason}"
            ) from e
        except TimeoutError as e:
            raise OllamaError("Таймаут: модель слишком долго думает.") from e

        try:
            data = json.loads(raw)
            return data["message"]["content"].strip() or "(пустой ответ)"
        except (KeyError, json.JSONDecodeError) as e:
            raise OllamaError(f"Некорректный ответ сервера: {raw[:200]}") from e

    def list_models(self):
        req = urllib.request.Request(f"{self.base_url}/api/tags")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            raise OllamaError(str(e)) from e
