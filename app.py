
import os

import psycopg
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
notes = []


def initialize_database():
    if DATABASE_URL:
        with psycopg.connect(DATABASE_URL) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL
                )
            """)


initialize_database()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/notes", methods=["GET"])
def get_notes():
    if DATABASE_URL:
        with psycopg.connect(DATABASE_URL) as conn:
            rows = conn.execute(
                "SELECT id, text FROM notes ORDER BY id"
            ).fetchall()

        return jsonify([
            {"id": row[0], "text": row[1]} for row in rows
        ])

    return jsonify(notes)


@app.route("/notes", methods=["POST"])
def add_note():
    data = request.get_json() or {}
    note_text = data.get("text", "").strip()

    if not note_text:
        return jsonify(error="Note text is required"), 400

    if DATABASE_URL:
        with psycopg.connect(DATABASE_URL) as conn:
            row = conn.execute(
                "INSERT INTO notes (text) VALUES (%s) RETURNING id, text",
                (note_text,)
            ).fetchone()

        return jsonify({"id": row[0], "text": row[1]}), 201

    note = {
        "id": max((n["id"] for n in notes), default=0) + 1,
        "text": note_text
    }
    notes.append(note)
    return jsonify(note), 201


@app.route("/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json() or {}
    note_text = data.get("text", "").strip()

    if not note_text:
        return jsonify(error="Note text is required"), 400

    if DATABASE_URL:
        with psycopg.connect(DATABASE_URL) as conn:
            row = conn.execute(
                """
                UPDATE notes
                SET text = %s
                WHERE id = %s
                RETURNING id, text
                """,
                (note_text, note_id)
            ).fetchone()

        if row is None:
            return jsonify(error="Note not found"), 404

        return jsonify({"id": row[0], "text": row[1]})

    for note in notes:
        if note["id"] == note_id:
            note["text"] = note_text
            return jsonify(note)

    return jsonify(error="Note not found"), 404


@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    if DATABASE_URL:
        with psycopg.connect(DATABASE_URL) as conn:
            row = conn.execute(
                "DELETE FROM notes WHERE id = %s RETURNING id",
                (note_id,)
            ).fetchone()

        if row is None:
            return jsonify(error="Note not found"), 404

        return jsonify(message="Note deleted successfully")

    for note in notes:
        if note["id"] == note_id:
            notes.remove(note)
            return jsonify(message="Note deleted successfully")

    return jsonify(error="Note not found"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
