import os
import time
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Variables d'environnement
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", 5432)
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")


# Connexion avec retry
def get_db_connection():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME
            )
            return conn
        except Exception as e:
            print("⏳ Waiting for PostgreSQL...", e)
            time.sleep(2)


# Initialisation DB (table)
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL
    );
    """)

    conn.commit()
    cur.close()
    conn.close()


# Appel au démarrage
init_db()


# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200


# GET /tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, title FROM tasks;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    tasks = [{"id": r[0], "title": r[1]} for r in rows]
    return jsonify(tasks), 200


# POST /tasks
@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({"error": "Task must have a title"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tasks (title) VALUES (%s) RETURNING id;",
        (data["title"],)
    )
    task_id = cur.fetchone()[0]
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "id": task_id,
        "title": data["title"]
    }), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)