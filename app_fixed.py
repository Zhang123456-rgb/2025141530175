from flask import Flask, render_template, request, redirect, session, url_for
import os
import sqlite3
import hashlib
import uuid
import logging
import magic
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB

# ============ 路径配置 ============
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "users.db")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
ALLOWED_MIMES = {"image/jpeg", "image/png", "image/gif", "image/bmp", "image/webp"}

# ============ 日志配置（修复7：审计日志） ============
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
audit_logger = logging.getLogger("upload_audit")
audit_handler = logging.FileHandler(os.path.join(LOG_DIR, "upload_audit.log"), encoding="utf-8")
audit_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)


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
    c.execute("INSERT OR IGNORE INTO users (username, password, email, phone, balance, role) VALUES (?, ?, ?, ?, ?, ?)",
              ("admin", hash_pw("admin123"), "admin@example.com", "13800138000", 99999, "admin"))
    c.execute("INSERT OR IGNORE INTO users (username, password, email, phone, balance, role) VALUES (?, ?, ?, ?, ?, ?)",
              ("alice", hash_pw("alice2025"), "alice@example.com", "13900139001", 100, "user"))

    # 创建商品表
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    c.execute("INSERT OR IGNORE INTO products (id, name, price) VALUES (1, 'iPhone 15 Pro Max', 9999)")
    c.execute("INSERT OR IGNORE INTO products (id, name, price) VALUES (2, 'MacBook Pro 16', 19999)")
    c.execute("INSERT OR IGNORE INTO products (id, name, price) VALUES (3, 'AirPods Max', 3999)")
    c.execute("INSERT OR IGNORE INTO products (id, name, price) VALUES (4, 'iPad Pro 12.9', 7999)")

    try:
        c.execute("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0")
    except:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    except:
        pass
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


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "username" not in session:
        return redirect("/login")

    upload_msg = None
    upload_success = False
    file_url = None
    filename_display = None

    if request.method == "POST":
        if "file" not in request.files:
            upload_msg = "没有选择文件"
        else:
            f = request.files["file"]
            if f.filename == "":
                upload_msg = "文件名为空"
            else:
                original_name = f.filename

                # ========== 修复1：文件后缀白名单检查 ==========
                ext = os.path.splitext(original_name)[1].lower()
                if ext not in ALLOWED_EXTENSIONS:
                    upload_msg = f"不支持的文件类型：{ext}，仅允许图片文件"
                    audit_logger.warning(f"上传被拒：[后缀不合法] 用户={session['username']} 文件={original_name} ext={ext}")
                    return render_template("upload_fixed.html", upload_msg=upload_msg)

                # ========== 修复2+5：后端MIME类型检测 ==========
                f.stream.seek(0)
                mime_type = magic.from_buffer(f.read(2048), mime=True)
                f.stream.seek(0)
                if mime_type not in ALLOWED_MIMES:
                    upload_msg = f"文件内容不合法（检测到 {mime_type}），仅允许图片文件"
                    audit_logger.warning(f"上传被拒：[MIME不合法] 用户={session['username']} 文件={original_name} mime={mime_type}")
                    return render_template("upload_fixed.html", upload_msg=upload_msg)

                # ========== 修复4：UUID重命名 ==========
                safe_filename = uuid.uuid4().hex + ext

                # ========== 修复3+8：清理路径，确保在uploads内 ==========
                safe_path = Path(UPLOAD_DIR).resolve()
                safe_path.mkdir(parents=True, exist_ok=True)
                save_path = (safe_path / safe_filename).resolve()

                # 二次校验：确认路径仍在UPLOAD_DIR内（防止Path解析绕过）
                if not str(save_path).startswith(str(safe_path)):
                    upload_msg = "文件名不合法"
                    audit_logger.error(f"上传被拒：[路径穿越] 用户={session['username']} 原始文件名={original_name}")
                    return render_template("upload_fixed.html", upload_msg=upload_msg)

                f.save(str(save_path))
                file_url = url_for("static", filename=f"uploads/{safe_filename}")
                upload_success = True
                upload_msg = "上传成功！"
                filename_display = safe_filename

                # ========== 修复7：审计日志 ==========
                audit_logger.info(
                    f"上传成功：用户={session['username']} "
                    f"原始文件={original_name} "
                    f"保存为={safe_filename} "
                    f"大小={os.path.getsize(save_path)}字节 "
                    f"MIME={mime_type} "
                    f"IP={request.remote_addr}"
                )

    return render_template("upload_fixed.html",
                           upload_msg=upload_msg,
                           upload_success=upload_success,
                           file_url=file_url,
                           filename=filename_display)


@app.route("/shop", methods=["GET"])
def shop():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, price FROM products")
    products = [dict(r) for r in c.fetchall()]
    conn.close()
    return render_template("shop_fixed.html", products=products)


@app.route("/cart", methods=["POST"])
def cart():
    if "username" not in session:
        return redirect("/login")

    product_id = request.form.get("product_id")
    quantity = request.form.get("quantity", "1")

    # ✅ 修复：价格从服务器数据库获取，不信任客户端
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT name, price FROM products WHERE id = ?", (product_id,))
    product = c.fetchone()
    conn.close()

    if not product:
        return "商品不存在"

    price = product["price"]
    total = price * int(quantity)

    return render_template("cart_fixed.html",
                           product_name=product["name"],
                           price=price,
                           quantity=quantity,
                           total=total)


@app.route("/admin", methods=["GET"])
def admin_panel():
    # ✅ 修复：检查管理员权限
    username = session.get("username")
    if not username:
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    if not row or row["role"] != "admin":
        audit_logger.warning(f"越权访问被拒：用户={username} 尝试访问管理面板")
        return "权限不足，仅管理员可访问"

    c.execute("SELECT id, username, email, balance FROM users")
    users = [dict(r) for r in c.fetchall()]
    conn.close()
    return render_template("admin_fixed.html", users=users)


@app.route("/admin/delete-user", methods=["POST"])
def admin_delete_user():
    # ✅ 修复：检查管理员权限
    username = session.get("username")
    if not username:
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    if not row or row["role"] != "admin":
        audit_logger.warning(f"越权删除被拒：用户={username}")
        return "权限不足"

    user_id = request.form.get("user_id")
    # ✅ 参数化查询
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()

    audit_logger.info(f"管理员={username} 删除了用户ID={user_id}")
    conn.close()
    return redirect("/admin")


@app.route("/profile", methods=["GET"])
def profile():
    if "username" not in session:
        return redirect("/login")

    user_id = request.args.get("user_id")
    if not user_id:
        return "缺少user_id参数"

    # ✅ 修复：验证当前用户只能查看自己的资料
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return "用户不存在"

    # 只有admin可以查看所有用户，普通用户只能看自己
    c.execute("SELECT role FROM users WHERE username = ?", (session["username"],))
    cur_user = c.fetchone()
    if cur_user["role"] != "admin" and row["username"] != session["username"]:
        audit_logger.warning(f"IDOR越权被拒：用户={session['username']} 尝试查看user_id={user_id}")
        conn.close()
        return "权限不足，只能查看自己的资料"

    c.execute("SELECT id, username, email, phone, balance FROM users WHERE id = ?", (user_id,))
    profile_user = dict(c.fetchone())
    conn.close()

    return render_template("profile_fixed.html", user=profile_user)


@app.route("/recharge", methods=["POST"])
def recharge():
    if "username" not in session:
        return redirect("/login")

    user_id = request.form.get("user_id")
    amount = request.form.get("amount")

    # ✅ 修复：验证当前用户只能给自己充值
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return "用户不存在"
    if row["username"] != session["username"]:
        return "不能为其他用户充值"

    # ✅ 修复：校验amount为正数
    try:
        amount = float(amount)
        if amount <= 0:
            return "充值金额必须为正数"
    except ValueError:
        return "金额格式错误"

    c.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
    conn.commit()

    audit_logger.info(f"充值成功：用户={session['username']} 金额=+{amount}")
    conn.close()
    return redirect(f"/profile?user_id={user_id}")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5001)
