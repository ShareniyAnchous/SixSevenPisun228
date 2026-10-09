"""
Solar — AI-ассистент. Точка входа Kivy-приложения.
Способ A: APK = тонкий клиент, модель работает на Ollama (ваш ПК) по локальной сети.
"""
import json
import os
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from ollama_client import OllamaClient, OllamaError

BOT_NAME = "Solar"
SYSTEM_PROMPT = (
    "Ты — Solar, дружелюбный и лаконичный AI-ассистент. "
    "Отвечай на языке пользователя. Помогай с кодом, текстами и вопросами."
)
CONFIG_PATH = os.path.join(os.path.expanduser("~"), "solar_config.json")
DEFAULT_HOST = "http://192.168.1.100:11434"  # замените на IP вашего ПК
DEFAULT_MODEL = "qwen2.5:3b"


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}
    return {
        "host": cfg.get("host", DEFAULT_HOST),
        "model": cfg.get("model", DEFAULT_MODEL),
    }


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f)
    except Exception:
        pass


class ChatLog(ScrollView):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bar_width = 20
        self.content = BoxLayout(orientation="vertical", size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))
        self.add_widget(self.content)

    def add_msg(self, who, text):
        color = {"user": "7df9ff", "bot": "ffd479", "sys": "ff6b6b"}[who]
        lbl = Label(
            text=f"[b][color={color}]{who.upper()}:[/color][/b] {text}",
            markup=True, halign="left", valign="top",
            size_hint_y=None, padding=(12, 8),
        )
        lbl.bind(texture_size=lbl.setter("size"))
        self.content.add_widget(lbl)
        Clock.schedule_once(lambda *_: self.scroll_to(lbl, padding=10), 0.1)


class SolarApp(App):
    title = BOT_NAME

    def __init__(self, **kw):
        super().__init__(**kw)
        self.cfg = load_config()
        self.client = OllamaClient(self.cfg["host"], self.cfg["model"])
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.busy = False

    def build(self):
        Window.softinput_mode = "below_target"
        root = BoxLayout(orientation="vertical", padding=8, spacing=8)

        header = BoxLayout(size_hint_y=None, height=44, spacing=8)
        self.title_lbl = Label(
            text=f"☀ {BOT_NAME}  ·  {self.cfg['model']}",
            bold=True, color=(1, 0.83, 0.47, 1),
            halign="left", valign="middle",
        )
        settings_btn = TextInput(
            text="⚙ Настройки", readonly=True, size_hint_x=None, width=120,
            background_color=(0.15, 0.15, 0.2, 1), foreground_color=(1, 1, 1, 1),
        )
        settings_btn.bind(on_touch_down=self.open_settings)
        header.add_widget(self.title_lbl)
        header.add_widget(settings_btn)

        self.log = ChatLog(size_hint_y=1)
        input_row = BoxLayout(size_hint_y=None, height=56, spacing=8)
        self.input = TextInput(
            hint_text=f"Напишите {BOT_NAME}…", multiline=False,
            font_size=18, foreground_color=(1, 1, 1, 1),
        )
        send_btn = TextInput(
            text="➤", readonly=True, size_hint_x=None, width=64, font_size=22,
            background_color=(0.9, 0.6, 0.1, 1), foreground_color=(0, 0, 0, 1),
        )
        send_btn.bind(on_touch_down=lambda *a: self.send())
        self.input.bind(on_text_validate=lambda *a: self.send())
        input_row.add_widget(self.input)
        input_row.add_widget(send_btn)

        root.add_widget(header)
        root.add_widget(self.log)
        root.add_widget(input_row)
        self.log.add_msg("bot", f"Привет! Я {BOT_NAME}. Спрашивайте что угодно.")
        return root

    # ---------- логика чата ----------
    def send(self, *a):
        text = self.input.text.strip()
        if not text or self.busy:
            return
        self.input.text = ""
        self.busy = True
        self.log.add_msg("user", text)
        self.history.append({"role": "user", "content": text})
        threading.Thread(target=self._worker, args=(text,), daemon=True).start()

    def _worker(self, user_text):
        try:
            reply = self.client.chat(self.history)
            self.history.append({"role": "assistant", "content": reply})
            Clock.schedule_once(lambda *_: self._on_reply(reply))
        except OllamaError as e:
            Clock.schedule_once(lambda *_: self._on_error(str(e)))

    def _on_reply(self, reply):
        self.busy = False
        self.log.add_msg("bot", reply)

    def _on_error(self, msg):
        self.busy = False
        self.history.pop()  # откат последнего сообщения пользователя
        self.log.add_msg("sys", f"Ошибка: {msg}")

    # ---------- настройки ----------
    def open_settings(self, instance, touch):
        if not instance.collide_point(*touch.pos):
            return
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        host_inp = TextInput(text=self.cfg["host"], size_hint_y=None, height=48)
        model_inp = TextInput(text=self.cfg["model"], size_hint_y=None, height=48)
        ok = TextInput(text="Сохранить", readonly=True, size_hint_y=None, height=48,
                       background_color=(0.9, 0.6, 0.1, 1), foreground_color=(0, 0, 0, 1))

        def close(*a):
            self.cfg["host"] = host_inp.text.strip() or DEFAULT_HOST
            self.cfg["model"] = model_inp.text.strip() or DEFAULT_MODEL
            save_config(self.cfg)
            self.client = OllamaClient(self.cfg["host"], self.cfg["model"])
            self.title_lbl.text = f"☀ {BOT_NAME}  ·  {self.cfg['model']}"
            popup.dismiss()

        ok.bind(on_touch_down=close)
        box.add_widget(Label(text="Ollama URL (http://IP_ПК:11434)", size_hint_y=None, height=30))
        box.add_widget(host_inp)
        box.add_widget(Label(text="Модель", size_hint_y=None, height=30))
        box.add_widget(model_inp)
        box.add_widget(ok)
        popup = Popup(title="Настройки Solar", content=box, size_hint=(0.9, 0.5))
        popup.open()


if __name__ == "__main__":
    SolarApp().run()
