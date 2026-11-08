import time
import json
import urllib.request
import urllib.parse
from datetime import datetime

BOT_TOKEN = "9003240042:AAF4bXvajM6qoJzAs6UdfCA-pI8m4PjpxG8"
ADMIN_CHAT_ID = 1007729293

user_states = {}

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if keyboard:
        payload["reply_markup"] = keyboard
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception as e:
        print(f"Ошибка отправки: {e}")

MAIN_KEYBOARD = {
    "keyboard": [
        [{"text": "🔌 Подключение"}, {"text": "ℹ️ О работе бота"}],
        [{"text": "💡 Предложить идею"}, {"text": "🆔 Мой ID"}],
        [{"text": "🗑 Отключить уведомления"}]
    ],
    "resize_keyboard": True
}

CANCEL_KEYBOARD = {
    "keyboard": [[{"text": "❌ Отмена"}]],
    "resize_keyboard": True
}

def handle_update(update):
    msg = update.get("message")
    if not msg or "chat" not in msg:
        return

    chat_id = msg["chat"]["id"]
    user_name = msg.get("from", {}).get("first_name", "пользователь")
    username = msg.get("from", {}).get("username", "")
    text = msg.get("text", "").strip()
    lower = text.lower()

    if user_states.get(chat_id) == "WAITING_IDEA":
        if lower in ["❌ отмена", "/cancel", "отмена"]:
            user_states.pop(chat_id, None)
            send_message(chat_id, "Ввод отменен.", MAIN_KEYBOARD)
            return

        user_states.pop(chat_id, None)
        user_display = f"@{username}" if username else user_name
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        admin_alert = (
            f"💡 <b>Новая идея для бота!</b>\n"
            f"👤 <b>От:</b> {user_display} (ID: <code>{chat_id}</code>)\n"
            f"🕒 <b>Время:</b> {time_str}\n\n"
            f"📝 <b>Текст предложения:</b>\n"
            f"<i>{text}</i>"
        )
        send_message(ADMIN_CHAT_ID, admin_alert)
        send_message(chat_id, "🎉 <b>Спасибо за предложение!</b>\n\nВаша идея передана автору бота.", MAIN_KEYBOARD)
        return

    if lower in ["/idea", "/suggest", "предложить идею", "💡 предложить идею"]:
        user_states[chat_id] = "WAITING_IDEA"
        prompt = (
            "💡 <b>Предложка для идей и предложений</b>\n\n"
            "Напишите ваше пожелание или идею следующим сообщением.\n"
            "<i>(Нажмите «❌ Отмена», если передумали)</i>"
        )
        send_message(chat_id, prompt, CANCEL_KEYBOARD)
        return

    if lower in ["/info", "/about", "о работе бота", "ℹ️ о работе бота"]:
        about = (
            "ℹ️ <b>О работе бота:</b>\n\n"
            "🤖 <b>Назначение:</b> мгновенные уведомления, когда автономные ИИ-агенты заканчивают длинные задачи.\n\n"
            "⚡ <b>Расход токенов:</b> <b>0 токенов (бесплатно).</b> Уведомления не используют LLM, а работают через системные хуки ОС.\n\n"
            "🔒 <b>Приватность:</b> Бот хранит только Chat ID. Удалить данные можно в один клик кнопкой «🗑 Отключить»."
        )
        send_message(chat_id, about, MAIN_KEYBOARD)
        return

    if lower in ["/connect", "подключение", "🔌 подключение", "/help"]:
        guide = (
            f"🔌 <b>Инструкция по подключению ИИ-агентов</b>\n\n"
            f"Ваш Chat ID: <code>{chat_id}</code>\n"
            f"Токен бота: <code>{BOT_TOKEN}</code>\n\n"
            f"───────────────────\n"
            f"🔹 <b>Google Antigravity:</b>\n"
            f"В <code>~/.gemini/config/hooks.json</code> добавьте хук <code>Stop</code>.\n\n"
            f"🔹 <b>Claude Code:</b>\n"
            f"<code>claude ; python notify.py 'Claude закончил'</code>\n\n"
            f"🔹 <b>Aider / Cursor:</b>\n"
            f"<code>aider ; python notify.py 'Aider закончил'</code>\n\n"
            f"🔹 <b>cURL (одной строкой):</b>\n"
            f"<code>curl -X POST \"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage\" "
            f"-d \"chat_id={chat_id}&text=✅ Агент завершил работу!\"</code>"
        )
        send_message(chat_id, guide, MAIN_KEYBOARD)
        return

    if lower in ["/id", "id", "🆔 мой id", "мой id"]:
        send_message(chat_id, f"🆔 Ваш Telegram Chat ID: <code>{chat_id}</code>", MAIN_KEYBOARD)
        return

    if lower in ["/delete", "удалить", "отключить", "🗑 отключить уведомления"]:
        send_message(chat_id, "🗑 <b>Уведомления отключены!</b>\n\nЧтобы включить снова — нажмите «🔌 Подключение».", MAIN_KEYBOARD)
        return

    greeting = (
        f"👋 <b>Привет, {user_name}!</b>\n\n"
        f"Я бот для уведомлений о завершении работы ИИ-агентов.\n"
        f"🆔 Ваш Chat ID: <code>{chat_id}</code>\n\n"
        f"Выберите действие в меню ниже:"
    )
    send_message(chat_id, greeting, MAIN_KEYBOARD)

def main():
    print("🤖 Бот запущен в облаке и готов к работе...")
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?timeout=25&offset={offset}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    handle_update(update)
        except Exception as e:
            time.sleep(3)

if __name__ == "__main__":
    main()
