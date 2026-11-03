from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "replace-this-secret-before-deployment"
DB = Path(__file__).with_name("bugs.db")

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS bugs(id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL, priority TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Open', reporter TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

@app.route("/")
def index():
    with connect() as con:
        rows = con.execute("SELECT * FROM bugs ORDER BY id DESC").fetchall()
        if "bug-tracking-system" == "bug-tracking-system":
            stats = [con.execute("SELECT COUNT(*) FROM bugs").fetchone()[0],
                     con.execute("SELECT COUNT(*) FROM bugs WHERE status='Open'").fetchone()[0],
                     con.execute("SELECT COUNT(*) FROM bugs WHERE status='Resolved'").fetchone()[0]]
        elif "bug-tracking-system" == "student-task-manager":
            stats = [con.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],
                     con.execute("SELECT COUNT(*) FROM tasks WHERE completed=0").fetchone()[0],
                     con.execute("SELECT COUNT(*) FROM tasks WHERE completed=1").fetchone()[0]]
        else:
            stats = [con.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE entry_type='Income'").fetchone()[0],
                     con.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE entry_type='Expense'").fetchone()[0],
                     con.execute("SELECT COALESCE(SUM(CASE WHEN entry_type='Income' THEN amount ELSE -amount END),0) FROM expenses").fetchone()[0]]
    return render_template("index.html", rows=rows, stats=stats)

@app.route("/add", methods=["GET","POST"])
def add():
    if request.method == "POST":
        values = [request.form.get("title","").strip(), request.form.get("description","").strip(), request.form.get("priority","Medium"), request.form.get("reporter","").strip()]
        if not all(str(v).strip() for v in values):
            flash("Please complete all fields.", "error")
            return redirect(url_for("add"))
        if values[2] not in ("Low","Medium","High"): values[2]="Medium"
        with connect() as con:
            con.execute("INSERT INTO bugs(title,description,priority,reporter) VALUES(?,?,?,?)", values)
        flash("Saved successfully.", "success")
        return redirect(url_for("index"))
    return render_template("form.html")

@app.route("/<int:item_id>/action", methods=["POST"])
def action(item_id):
    with connect() as con:
        status=request.form.get("status","Open")
        if status not in ("Open","In Progress","Resolved"): status="Open"
        con.execute("UPDATE bugs SET status=? WHERE id=?", (status,item_id))
    flash("Record updated.", "success")
    return redirect(url_for("index"))

@app.route("/<int:item_id>/delete", methods=["POST"])
def delete(item_id):
    with connect() as con:
        con.execute("DELETE FROM bugs WHERE id=?", (item_id,))
    flash("Record deleted.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
