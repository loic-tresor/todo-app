from flask import Flask, render_template_string, request, redirect
import requests
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Todo App</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; }
    h1 { color: #333; }
    input[type=text] { width: 70%; padding: 8px; font-size: 16px; }
    button { padding: 8px 16px; font-size: 16px; cursor: pointer; }
    ul { list-style: none; padding: 0; }
    li { display: flex; align-items: center; gap: 10px; padding: 8px; border-bottom: 1px solid #eee; }
    .done { text-decoration: line-through; color: #aaa; }
    .del { color: red; cursor: pointer; background: none; border: none; font-size: 18px; }
  </style>
</head>
<body>
  <h1>Mes tâches</h1>
  <form method="POST" action="/add">
    <input type="text" name="title" placeholder="Nouvelle tâche..." required>
    <button type="submit">Ajouter</button>
  </form>
  <ul>
    {% for task in tasks %}
    <li>
      <form method="POST" action="/toggle/{{ task.id }}">
        <input type="checkbox" onchange="this.form.submit()" {% if task.done %}checked{% endif %}>
      </form>
      <span class="{% if task.done %}done{% endif %}">{{ task.title }}</span>
      <form method="POST" action="/delete/{{ task.id }}" style="margin-left:auto">
        <button class="del" type="submit">✕</button>
      </form>
    </li>
    {% endfor %}
  </ul>
</body>
</html>
"""

@app.route("/")
def index():
    logger.info("GET / called")
    try:
        resp = requests.get(f"{BACKEND_URL}/tasks", timeout=5)
        tasks = resp.json()
    except Exception as e:
        logger.error(f"Backend unreachable: {e}")
        tasks = []
    return render_template_string(HTML, tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    requests.post(f"{BACKEND_URL}/tasks", json={"title": title}, timeout=5)
    return redirect("/")

@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle(task_id):
    resp = requests.get(f"{BACKEND_URL}/tasks", timeout=5)
    tasks = resp.json()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task:
        requests.put(f"{BACKEND_URL}/tasks/{task_id}",
                     json={"done": not task["done"]}, timeout=5)
    return redirect("/")

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    requests.delete(f"{BACKEND_URL}/tasks/{task_id}", timeout=5)
    return redirect("/")

@app.route("/health")
def health():
    return {"status": "ok", "service": "frontend"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
