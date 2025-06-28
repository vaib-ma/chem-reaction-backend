from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

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
        
        # Create table for blog posts
        conn.execute('''CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            views INTEGER DEFAULT 0
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
            "SELECT reaction, explanation, video_url, submitted_at FROM reactions ORDER BY id DESC LIMIT 20"
        ).fetchall()
    return jsonify([
        {
            "reaction": row[0],
            "explanation": row[1],
            "video_url": row[2],
            "submitted_at": row[3]
        } for row in rows
    ])

@app.route('/blog/posts', methods=['GET'])
def get_blog_posts():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, title, content, image_url, created_at, views FROM blog_posts ORDER BY created_at DESC"
        ).fetchall()
    return jsonify([
        {
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "image_url": row[3],
            "created_at": row[4],
            "views": row[5]
        } for row in rows
    ])

@app.route('/blog/post/<int:post_id>', methods=['GET'])
def get_blog_post(post_id):
    with sqlite3.connect(DB_PATH) as conn:
        # Increment view count
        conn.execute(
            "UPDATE blog_posts SET views = views + 1 WHERE id = ?",
            (post_id,)
        )
        post = conn.execute(
            "SELECT id, title, content, image_url, created_at, views FROM blog_posts WHERE id = ?",
            (post_id,)
        ).fetchone()
    if post:
        return jsonify({
            "id": post[0],
            "title": post[1],
            "content": post[2],
            "image_url": post[3],
            "created_at": post[4],
            "views": post[5]
        })
    return jsonify({"error": "Post not found"}), 404

@app.route('/blog/create', methods=['POST'])
def create_blog_post():
    data = request.get_json()
    required_fields = ['title', 'content']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
        
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO blog_posts (title, content, image_url) VALUES (?, ?, ?)",
            (data['title'], data['content'], data.get('image_url', ''))
        )
    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
