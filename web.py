from flask import Flask, render_template_string, request, jsonify
import json
import os
from difflib import SequenceMatcher

app = Flask(__name__)

class SimpleChatBot:
    def __init__(self, memory_file='memory.json'):
        self.memory_file = memory_file
        self.data = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"responses": {}, "unknown": []}

    def save_memory(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def learn(self, question, answer):
        self.data["responses"][question.strip()] = answer.strip()
        self.save_memory()

    def learn_from_file(self, filename):
        if not os.path.exists(filename):
            return 0
        count = 0
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '|' not in line:
                    continue
                parts = line.split('|')
                if len(parts) == 2:
                    q, a = parts
                    self.data["responses"][q.strip()] = a.strip()
                    count += 1
        self.save_memory()
        return count

    def find_best_match(self, message):
        best_score = 0
        best_answer = None
        for q, a in self.data["responses"].items():
            score = SequenceMatcher(None, message, q).ratio()
            if score > best_score:
                best_score = score
                best_answer = a
        return best_answer, best_score

    def respond(self, message):
        message = message.strip()
        if message in self.data["responses"]:
            return self.data["responses"][message]
        answer, score = self.find_best_match(message)
        if score > 0.6:
            return answer
        self.data["unknown"].append(message)
        self.save_memory()
        return "نمی‌دونم. بهم یاد بده چی بگم؟"

bot = SimpleChatBot()
count = bot.learn_from_file('data.txt')
print(f"✅ {count} سوال و جواب از فایل data.txt یاد گرفته شد!")

HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>چت‌بات من</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: Tahoma, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px;
        }
        .chat-container {
            width: 100%;
            max-width: 500px;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 20px;
            font-weight: bold;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            justify-content: flex-start;
        }
        .message.bot {
            justify-content: flex-end;
        }
        .bubble {
            max-width: 75%;
            padding: 12px 18px;
            border-radius: 18px;
            font-size: 15px;
            line-height: 1.5;
        }
        .user .bubble {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 5px;
        }
        .bot .bubble {
            background: white;
            color: #333;
            border-bottom-left-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .input-area {
            padding: 15px;
            background: white;
            display: flex;
            gap: 10px;
            border-top: 1px solid #eee;
        }
        input {
            flex: 1;
            padding: 12px 18px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 15px;
            outline: none;
            font-family: Tahoma, sans-serif;
            transition: border 0.3s;
        }
        input:focus {
            border-color: #667eea;
        }
        button {
            padding: 12px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 15px;
            cursor: pointer;
            font-family: Tahoma, sans-serif;
            font-weight: bold;
            transition: transform 0.2s;
        }
        button:active {
            transform: scale(0.95);
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">🤖 چت‌بات من</div>
        <div class="messages" id="messages">
            <div class="message bot">
                <div class="bubble">سلام! من چت‌بات تو هستم. چی می‌خوای بپرسی؟ 😊</div>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="پیامت رو بنویس..." autocomplete="off">
            <button onclick="sendMessage()">ارسال</button>
        </div>
    </div>

    <script>
        const messages = document.getElementById('messages');
        const input = document.getElementById('userInput');

        function addMessage(text, type) {
            const div = document.createElement('div');
            div.className = 'message ' + type;
            div.innerHTML = '<div class="bubble">' + text + '</div>';
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;
            addMessage(text, 'user');
            input.value = '';
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            const data = await res.json();
            addMessage(data.reply, 'bot');
        }

        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    reply = bot.respond(data['message'])
    return jsonify({'reply': reply})

if __name__ == '__main__':
    print("🌐 سرور روی http://localhost:5000 اجرا شد")
    print("برای خروج: CTRL+C")
    app.run(host='0.0.0.0', port=5000)
