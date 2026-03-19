import sqlite3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from groq import Groq
import wikipedia
import os  # Ye top par add karein agar nahi hai

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
SECRET_CREATOR_KEY = "hira786"

def init_db():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_info 
                 (id INTEGER PRIMARY KEY, name TEXT, university TEXT)''')
    c.execute("SELECT COUNT(*) FROM user_info")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO user_info (name, university) VALUES (?, ?)", 
                  ("User", "Green International University"))
    conn.commit()
    conn.close()

init_db()

def get_db_data():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute("SELECT name, university FROM user_info WHERE id=1")
    data = c.fetchone()
    conn.close()
    return {"name": data[0], "university": data[1]}

def update_db_name(new_name):
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute("UPDATE user_info SET name=? WHERE id=1", (new_name,))
    conn.commit()
    conn.close()

def get_jolly_ai_response(query):
    try:
        # Balanced Personality: Friendly but not annoying
        system_msg = (
            "You are a witty and jolly AI assistant. Your developer is Hira Midhat. "
            "Be cool, use a bit of humor, and be helpful. "
            "DO NOT over-praise Hira in every sentence. Only mention or thank her "
            "if the user specifically asks about her or who built you. "
            "Keep your tone natural and conversational."
        )
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": query}
            ],
        )
        return completion.choices[0].message.content
    except:
        return "I'm just vibing in this Royal Blue theme! What's on your mind?"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('message', '').strip()
    low_msg = msg.lower()
    user_info = get_db_data()

    # 1. Identity Verification
    if "what is my name" in low_msg or "do you know me" in low_msg:
        name = user_info['name']
        if name == "User":
            reply = "I don't have your name yet! Care to tell me, or use the Creator Key?"
        else:
            reply = f"Your name is {name}! How can I help you today?"

    # 2. Secret Access Key
    elif low_msg == SECRET_CREATOR_KEY:
        update_db_name("Hira Midhat")
        reply = "Access Granted! Welcome back, Creator Hira Midhat. Elite Mode activated!"

    # 3. Smart Name Handling (Length Check for 'Insult Protection')
    elif any(p in low_msg for p in ["my name is", "i am", "call me"]):
        if len(low_msg.split()) > 5: # It's a long sentence, not a name
            reply = get_jolly_ai_response(msg)
        else:
            name_part = msg.split("is")[-1] if "is" in low_msg else msg.split("am")[-1] if "am" in low_msg else msg.split("me")[-1]
            clean_name = name_part.strip().capitalize()
            update_db_name(clean_name)
            reply = f"Got it! Hello {clean_name}, I'll remember that. All wisdom belongs to Allah (SWT)."

    # 4. Specific Info Search
    elif any(k in low_msg for k in ["define", "history of", "explain"]):
        try:
            wikipedia.set_lang("en")
            q = low_msg.replace("define", "").replace("history of", "").strip()
            reply = wikipedia.summary(q, sentences=2)
        except:
            reply = get_jolly_ai_response(msg)
    
    # 5. General Jolly Chat
    else:
        reply = get_jolly_ai_response(msg)

    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True, port=5000)