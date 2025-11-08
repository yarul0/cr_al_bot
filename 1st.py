import os
import json
import requests
import websocket
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")      # НЕ хардкодити токени
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = float(os.getenv("THRESHOLD", "100"))


def send_telegram(msg):
    """Відправляє повідомлення в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Помилка надсилання в Telegram: {e}")

def on_open(ws):
    print("✅ Підключено до Binance WebSocket")
    send_telegram("🟢 Бот запущено! Відстеження BTC у реальному часі...")

def on_message(ws, message):
    global last_price
    data = json.loads(message)
    price = float(data['p'])

    if last_price is None:
        last_price = price
        return

    diff = price - last_price
    if abs(diff) >= THRESHOLD:
        direction = "⬆️ зросла" if diff > 0 else "⬇️ впала"
        msg = f"🚨 Ціна BTC {direction} на ${abs(diff):.2f}!\nНова ціна: ${price:.2f}"
        print(msg)
        send_telegram(msg)
        last_price = price  # оновлюємо базову ціну

def on_error(ws, error):
    print(f"❌ Помилка WebSocket: {error}")

def on_close(ws, close_status_code, close_msg):
    print("🔴 З’єднання закрито, спроба перепідключення...")
    run_websocket()  # автоперепідключення

def run_websocket():
    ws = websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/btcusdt@trade",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    import threading
    last_price = None

    # WebSocket в окремому потоці
    t = threading.Thread(target=run_websocket)
    t.start()
