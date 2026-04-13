from flask import Flask, jsonify, request
import psycopg2
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        database=os.environ.get("DB_NAME", "tododb"),
        user=os.environ.get("DB_USER", "todouser"),
        password=os.environ.get("DB_PASSWORD", "todopass")
    )

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            done BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    logger.info("Database initialized")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "backend"})

@app.route("/tasks", methods=["GET"])
def get_tasks():
    logger.info("GET /tasks called")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, done, created_at FROM tasks ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    tasks = [{"id": r[0], "title": r[1], "done": r[2], "created_at": str(r[3])} for r in rows]
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    title = data.get("title", "")
    logger.info(f"POST /tasks title={title}")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id", (title,))
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": task_id, "title": title, "done": False}), 201

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    done = data.get("done", False)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET done=%s WHERE id=%s", (done, task_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": task_id, "done": done})

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"deleted": task_id})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000)
