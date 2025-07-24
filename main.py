from flask import Flask, request
import os
import openai
import requests

app = Flask(__name__)  # ← энэ мөр маш чухал

@app.route("/", methods=["GET"])
def home():
    return "✅ Solomon Chatbot is Running"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = os.environ.get("FB_VERIFY_TOKEN")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == verify_token:
            return challenge, 200
        return "Invalid verification token", 403

    elif request.method == "POST":
        data = request.get_json()
        print("📨 Incoming:", data)

        try:
            messaging = data['entry'][0]['messaging'][0]
            sender_id = messaging['sender']['id']

            if 'postback' in messaging:
                message_text = messaging['postback']['title']
            elif 'message' in messaging:
                message_text = messaging['message']['text']
            else:
                return "No valid message", 200

        except Exception as e:
            print("⛔ Parse error:", e)
            return "Parse failed", 200

        openai.api_key = os.getenv("OPENAI_API_KEY")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message_text}]
            )
            reply_text = response.choices[0].message.content.strip()
        except Exception as e:
            print("⛔ GPT error:", e)
            reply_text = "Уучлаарай, алдаа гарлаа."

        fb_token = os.getenv("FB_PAGE_TOKEN")
        fb_url = f"https://graph.facebook.com/v19.0/me/messages?access_token={fb_token}"
        payload = {
            "recipient": {"id": sender_id},
            "message": {"text": reply_text}
        }
        headers = {"Content-Type": "application/json"}
        fb_response = requests.post(fb_url, json=payload, headers=headers)
        print("✅ FB Send Response:", fb_response.text)

        return "OK", 200

if __name__ == "__main__":
    app.run()

