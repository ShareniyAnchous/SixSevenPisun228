"""
ollama_web_compat.py — необязательная CORS-обёртка над Ollama.
Нужна ТОЛЬКО если вы делаете веб-интерфейс или нативный HTTP-клиент блокируется.
Для Kivy-клиента из этого репозитория НЕ требуется (urllib не шлёт CORS-запросов).

Запуск:  python ollama_web_compat.py   (прокси на :8080 -> Ollama на :11434)
"""
import http.server
import json
import urllib.request

UPSTREAM = "http://127.0.0.1:11434"
PORT = 8080


class Handler(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        req = urllib.request.Request(UPSTREAM + self.path, data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = resp.read()
            self.send_response(200)
        except Exception as e:
            data = json.dumps({"error": str(e)}).encode()
            self.send_response(502)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        with urllib.request.urlopen(UPSTREAM + self.path, timeout=30) as resp:
            data = resp.read()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    print(f"CORS-прокси: 0.0.0.0:{PORT} -> {UPSTREAM}")
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
