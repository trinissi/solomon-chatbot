from flask import Flask, request
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 🔐 Орчны хувьсагчуудаа ачааллах
load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "✅ Solomon Chatbot is Running"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # 🔐 Facebook верификэйшн
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == FB_VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Invalid token", 403

    elif request.method == "POST":
        data = request.get_json()
        print("📨 Incoming:", data)

        if data["object"] == "page":
            for entry in data["entry"]:
                messaging = entry.get("messaging", [])
                for message_event in messaging:
                    sender_id = message_event["sender"]["id"]

                    if "message" in message_event and "text" in message_event["message"]:
                        user_message = message_event["message"]["text"]
                        reply = get_chat_response(user_message)
                        send_message(sender_id, reply)

                    elif "postback" in message_event:
                        payload = message_event["postback"].get("payload")
                        if payload in ["GET_STARTED", "WELCOME_MESSAGE"]:
                            send_message(sender_id, "Сайн байна уу? Танд яаж туслах вэ? 😊")

        return "OK", 200

def get_chat_response(user_message):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Та тавилгын компаний ухаалаг туслах чатбот. Хэрэглэгчийн асуултад эелдэг бөгөөд тодорхой хариулаарай."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("⛔ GPT error:", e)
        return "Уучлаарай, сервер дээр GPT хариу өгсөнгүй."

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={FB_PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print("❌ FB Send Error:", response.text)
    else:
        print("✅ FB Send Response:", response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

