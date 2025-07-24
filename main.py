@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📨 Incoming:", data)

    # 🟡 Message parse
    try:
        messaging = data['entry'][0]['messaging'][0]
        sender_id = messaging['sender']['id']

        # ✳️ POSTBACK (Get Started) ирвэл
        if 'postback' in messaging:
            message_text = messaging['postback']['title']
        elif 'message' in messaging:
            message_text = messaging['message']['text']
        else:
            print("⚠️ No message text or postback")
            return "No text", 200

    except Exception as e:
        print("⛔ Message parse error:", e)
        return "Parse failed", 200

    print(f"💬 {sender_id}: {message_text}")

    # 🧠 GPT хариу
    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message_text}]
        )
        reply_text = response.choices[0].message.content.strip()
    except Exception as e:
        print("⛔ GPT error:", e)
        reply_text = "Уучлаарай, хариу боловсруулахад алдаа гарлаа."

    # 📩 Facebook Messenger-д буцааж бичих
    fb_token = os.getenv("FB_PAGE_TOKEN")
    send_url = f"https://graph.facebook.com/v19.0/me/messages?access_token={fb_token}"
    payload = {
        "recipient": {"id": sender_id},
        "message": {"text": reply_text}
    }
    headers = {"Content-Type": "application/json"}
    fb_response = requests.post(send_url, json=payload, headers=headers)

    print("✅ FB Send Response:", fb_response.text)

    return "OK", 200

