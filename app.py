from flask import Flask, render_template, request, redirect, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "dev-key-2025"

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
    # 插入默认用户
    c.execute("INSERT OR IGNORE INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)",
              ("admin", "admin123", "admin@example.com", "13800138000"))
    c.execute("INSERT OR IGNORE INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)",
              ("alice", "alice2025", "alice@example.com", "13900139001"))
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

    # 从数据库获取当前登录用户的完整信息（含密码）
    if username:
        conn = get_db()
        c = conn.cursor()
        # ⚠️ SQL注入漏洞：使用 f-string 拼接
        sql = f"SELECT id, username, password, email, phone FROM users WHERE username = '{username}'"
        print(f"[SQL] {sql}")
        try:
            c.execute(sql)
            row = c.fetchone()
            if row:
                user = dict(row)
        except Exception as e:
            print(f"[SQL ERROR] {e}")
        conn.close()

    # 搜索功能
    keyword = request.args.get("keyword", "")
    results = []
    sql = ""
    if keyword:
        # ⚠️ SQL注入漏洞：使用 f-string 拼接
        sql = f"SELECT id, username, email, phone FROM users WHERE username LIKE '%{keyword}%' OR email LIKE '%{keyword}%'"
        print(f"[SQL] {sql}")
        conn = get_db()
        try:
            c = conn.cursor()
            c.execute(sql)
            results = [list(r) for r in c.fetchall()]
        except Exception as e:
            print(f"[SQL ERROR] {e}")
            results = []
        finally:
            conn.close()

    return render_template("index.html", user=user, keyword=keyword, results=results)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # ⚠️ SQL注入漏洞：使用 f-string 拼接
        sql = f"SELECT id, username, password, email, phone FROM users WHERE username = '{username}' AND password = '{password}'"
        print(f"[SQL] {sql}")
        conn = get_db()
        try:
            c = conn.cursor()
            c.execute(sql)
            row = c.fetchone()
            if row:
                session["username"] = row["username"]
                user = dict(row)
                conn.close()
                return render_template("index.html", user=user)
            else:
                error = "用户名或密码错误！"
        except Exception as e:
            print(f"[SQL ERROR] {e}")
            error = f"系统错误：{e}"
        conn.close()

    return render_template("login.html", error=error)


@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("keyword", "")
    if not keyword:
        return redirect("/")

    # ⚠️ SQL注入漏洞：使用 f-string 拼接
    sql = f"SELECT id, username, email, phone FROM users WHERE username LIKE '%{keyword}%' OR email LIKE '%{keyword}%'"
    print(f"[SQL] {sql}")
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute(sql)
        results = [list(r) for r in c.fetchall()]
    except Exception as e:
        print(f"[SQL ERROR] {e}")
        results = []
    finally:
        conn.close()

    username = session.get("username")
    user = None
    if username:
        conn2 = get_db()
        c2 = conn2.cursor()
        try:
            c2.execute(f"SELECT id, username, password, email, phone FROM users WHERE username = '{username}'")
            row = c2.fetchone()
            if row:
                user = dict(row)
        except:
            pass
        conn2.close()

    return render_template("index.html", user=user, keyword=keyword, results=results)


@app.route("/register", methods=["GET", "POST"])
def register():
    message = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        email = request.form.get("email", "")
        phone = request.form.get("phone", "")

        # ⚠️ SQL注入漏洞：使用 f-string 拼接
        sql = f"INSERT INTO users (username, password, email, phone) VALUES ('{username}', '{password}', '{email}', '{phone}')"
        print(f"[SQL] {sql}")
        conn = get_db()
        try:
            c = conn.cursor()
            c.execute(sql)
            conn.commit()
            message = "注册成功，请登录"
            return render_template("login.html", error=message)
        except Exception as e:
            print(f"[SQL ERROR] {e}")
            message = f"注册失败：{e}"
        finally:
            conn.close()

    return render_template("register.html", message=message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
