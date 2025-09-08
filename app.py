import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load FAQs from JSON
with open("faq_data.json", "r", encoding="utf-8") as f:
    FAQ = json.load(f)

# Check if OpenAI API key exists
OPENAI = os.getenv("OPENAI_API_KEY") is not None

try:
    if OPENAI:
        from openai import OpenAI
        oai = OpenAI()
except Exception:
    OPENAI = False


def match_intent(text):
    t = text.lower()
    best = None
    best_score = 0
    for item in FAQ:
        score = 0
        for kw in item.get("keywords", []):
            if kw in t:
                score += 1
        if score > best_score:
            best_score = score
            best = item
    return best if best_score > 0 else None


def answer_from_ai(text):
    if not OPENAI:
        return None
    context = "\n".join([f"Q: {i['title']}\nA: {i['answer']}" for i in FAQ])
    prompt = (
        "You are a concise assistant answering only about Iron Lady leadership "
        "programs. Use the context. If the question is unrelated or lacks info, "
        "say you can answer about programs, duration, online/offline, certificates, "
        "and mentors.\n\n"
        f"Context:\n{context}\n\nUser: {text}"
    )
    try:
        r = oai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Answer in 1-3 sentences."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return None


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("home.html")  # Homepage now points to home.html


@app.route("/chat")
def chatbot_page():
    return render_template("chatbot.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    msg = str(data.get("message", "")).strip()
    if not msg:
        return jsonify({"reply": "Please type a question."})
    m = match_intent(msg)
    if m:
        return jsonify({"reply": m.get("answer", "")})
    ai = answer_from_ai(msg)
    if ai:
        return jsonify({"reply": ai})
    return jsonify(
        {
            "reply": "I can answer about programs offered, duration, "
            "online/offline mode, certificates, and mentors/coaches. "
            "Try asking one of these."
        }
    )


# ---------------- TO-DO APP ----------------
todos = []  # in-memory list

@app.route("/todos", methods=["GET"])
def get_todos():
    return jsonify(todos)

@app.route("/todos", methods=["POST"])
def add_todo():
    data = request.get_json()
    task = str(data.get("task", "")).strip()
    if not task:
        return jsonify({"error": "Task cannot be empty"}), 400
    todo = {"id": len(todos) + 1, "task": task}
    todos.append(todo)
    return jsonify(todo), 201

@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    data = request.get_json()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["task"] = data.get("task", todo["task"])
            return jsonify(todo)
    return jsonify({"error": "Todo not found"}), 404

@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    global todos
    todos = [t for t in todos if t["id"] != todo_id]
    return jsonify({"message": "Deleted"})


@app.route("/todo")
def todo_page():
    return render_template("todo.html")  # To-Do page


if __name__ == "__main__":
    app.run(debug=True)
