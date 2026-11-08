import os
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv('DATABASE_URL', '').strip()
USE_POSTGRES = DATABASE_URL.startswith(('postgres://', 'postgresql://'))


def get_postgres_url():
    # Render may provide postgres://; psycopg accepts postgresql://.
    if DATABASE_URL.startswith('postgres://'):
        return DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    return DATABASE_URL


def init_db():
    if USE_POSTGRES:
        import psycopg
        with psycopg.connect(get_postgres_url()) as con:
            con.execute('''
                CREATE TABLE IF NOT EXISTS scans (
                    id BIGSERIAL PRIMARY KEY,
                    message TEXT NOT NULL,
                    result VARCHAR(20) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    else:
        db_path = BASE_DIR / 'smartmail.db'
        with sqlite3.connect(db_path) as con:
            con.execute('''
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    result TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')


def classify(text):
    # Temporary demonstration rule only. Step 2 will replace this with a trained ML model.
    keywords = ['free prize', 'claim now', 'you won', 'urgent winner', 'click here', 'lottery', 'cash reward']
    return 'Spam' if any(keyword in text.lower() for keyword in keywords) else 'Not Spam'


def save_scan(message, result):
    if USE_POSTGRES:
        import psycopg
        with psycopg.connect(get_postgres_url()) as con:
            con.execute('INSERT INTO scans (message, result) VALUES (%s, %s)', (message, result))
    else:
        with sqlite3.connect(BASE_DIR / 'smartmail.db') as con:
            con.execute('INSERT INTO scans (message, result) VALUES (?, ?)', (message, result))


def fetch_history():
    if USE_POSTGRES:
        import psycopg
        from psycopg.rows import dict_row
        with psycopg.connect(get_postgres_url(), row_factory=dict_row) as con:
            rows = con.execute('SELECT id, message, result, created_at FROM scans ORDER BY id DESC LIMIT 20').fetchall()
            total = con.execute('SELECT COUNT(*) AS count FROM scans').fetchone()['count']
            spam = con.execute("SELECT COUNT(*) AS count FROM scans WHERE result = 'Spam'").fetchone()['count']
            history = [dict(row, created_at=row['created_at'].isoformat()) for row in rows]
    else:
        with sqlite3.connect(BASE_DIR / 'smartmail.db') as con:
            con.row_factory = sqlite3.Row
            rows = con.execute('SELECT id, message, result, created_at FROM scans ORDER BY id DESC LIMIT 20').fetchall()
            total = con.execute('SELECT COUNT(*) FROM scans').fetchone()[0]
            spam = con.execute("SELECT COUNT(*) FROM scans WHERE result = 'Spam'").fetchone()[0]
            history = [dict(row) for row in rows]
    return history, total, spam


@app.route('/')
def home():
    return render_template('index.html')


@app.get('/health')
def health():
    return jsonify(status='ok', database='postgresql' if USE_POSTGRES else 'sqlite')


@app.post('/api/predict')
def predict():
    data = request.get_json(silent=True) or {}
    message = str(data.get('message', '')).strip()
    if not message or len(message) > 10000:
        return jsonify(error='Enter a message between 1 and 10,000 characters.'), 400
    result = classify(message)
    save_scan(message, result)
    return jsonify(
        result=result,
        mode='demo',
        notice='Keyword-based demo only; the trained ML model will be added in Step 2.'
    )


@app.get('/api/history')
def history():
    scans, total, spam = fetch_history()
    return jsonify(history=scans, total=total, spam=spam, safe=total - spam)


# Create the database table when the web service starts.
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=False)
