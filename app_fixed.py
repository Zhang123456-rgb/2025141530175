from flask import Flask, render_template, request, redirect, session
import os
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# ============ SQLite 数据库初始化 ============
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "users.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            phone TEXT
        )
    """)
    def hash_pw(pwd):
        return hashlib.sha256(pwd.encode()).hexdigest()

    c.execute("INSERT OR IGNORE INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)",
              ("admin", hash_pw("admin123"), "admin@example.com", "13800138000"))
    c.execute("INSERT OR IGNORE INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)",
              ("alice", hash_pw("alice2025"), "alice@example.com", "13900139001"))
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    username = session.get("username")
    user = None
    if username:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id, username, email, phone FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if row:
            user = dict(row)
        conn.close()

    keyword = request.args.get("keyword", "")
    results = []
    if keyword:
        search_term = f"%{keyword}%"
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id, username, email, phone FROM users WHERE username LIKE ? OR email LIKE ?",
                  (search_term, search_term))
        results = [list(r) for r in c.fetchall()]
        conn.close()

    return render_template("index_fixed.html", user=user, keyword=keyword, results=results)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id, username, password, email, phone FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()

        if row and row["password"] == hashlib.sha256(password.encode()).hexdigest():
            session["username"] = row["username"]
            user = {"id": row["id"], "username": row["username"], "email": row["email"], "phone": row["phone"]}
            return render_template("index_fixed.html", user=user)
        else:
            error = "用户名或密码错误！"

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    message = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        email = request.form.get("email", "")
        phone = request.form.get("phone", "")

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        conn = get_db()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)",
                      (username, hashed_pw, email, phone))
            conn.commit()
            message = "注册成功，请登录"
            return render_template("login.html", error=message)
        except Exception as e:
            message = f"注册失败：{e}"
        finally:
            conn.close()

    return render_template("register.html", message=message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
