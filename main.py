from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Solomon Chatbot is Running"

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        verify_token = os.getenv("FB_VERIFY_TOKEN")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == verify_token:
            return challenge, 200
        return "Invalid token", 403

    elif request.method == "POST":
        data = request.get_json()
        print(data)  # Түр зуур лог
        return "OK", 200

if __name__ == "__main__":
    app.run()
