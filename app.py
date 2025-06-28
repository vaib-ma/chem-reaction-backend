from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os


app = Flask(__name__)
CORS(app)

DB_PATH = 'reactions.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reaction TEXT NOT NULL,
            explanation TEXT,
            video_url TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

init_db()

@app.route('/submit', methods=['POST'])
def submit_reaction():
    data = request.get_json()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO reactions (reaction, explanation, video_url) VALUES (?, ?, ?)",
            (data['reaction'], data.get('explanation', ''), data.get('video_url', ''))
        )
    return jsonify({"status": "success"})

@app.route('/reactions', methods=['GET'])
def get_reactions():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT reaction, explanation, video_url, submitted_at FROM reactions ORDER BY id DESC"
        ).fetchall()
    return jsonify([
        {
            "reaction": row[0],
            "explanation": row[1],
            "video_url": row[2],
            "submitted_at": row[3]
        } for row in rows
    ])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
