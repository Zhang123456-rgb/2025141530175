from flask import Flask, render_template, request, redirect, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "dev-key-2025"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB

# ============ SQLite 数据库初始化 ============
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "users.db")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")

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
            phone TEXT,
            balance REAL DEFAULT 0
        )
    """)
    # 插入默认用户
    c.execute("INSERT OR IGNORE INTO users (username, password, email, phone, balance) VALUES (?, ?, ?, ?, ?)",
              ("admin", "admin123", "admin@example.com", "13800138000", 99999))
    c.execute("INSERT OR IGNORE INTO users (username, password, email, phone, balance) VALUES (?, ?, ?, ?, ?)",
              ("alice", "alice2025", "alice@example.com", "13900139001", 100))

    # 创建商品表
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    # 插入默认商品
    c.execute("INSERT OR IGNORE INTO products (id, name, price) VALUES (1, 'iPhone 15 Pro Max', 9999)")
    c.execute("INSERT OR IGNORE INTO products (id, name, price) VALUES (2, 'MacBook Pro 16', 19999)")
    c.execute("INSERT OR IGNORE INTO products (id, name, price) VALUES (3, 'AirPods Max', 3999)")
    c.execute("INSERT OR IGNORE INTO products (id, name, price) VALUES (4, 'iPad Pro 12.9', 7999)")

    # 兼容旧表
    try:
        c.execute("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0")
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


@app.route("/upload", methods=["GET", "POST"])
def upload():
    # 需要登录才能访问
    if "username" not in session:
        return redirect("/login")

    upload_msg = None
    upload_success = False
    file_url = None
    filename = None

    if request.method == "POST":
        if "file" not in request.files:
            upload_msg = "没有选择文件"
        else:
            f = request.files["file"]
            if f.filename == "":
                upload_msg = "文件名为空"
            else:
                # ⚠️ 不安全：使用用户原始文件名，不做任何检查
                filename = f.filename
                save_path = os.path.join(UPLOAD_DIR, filename)
                f.save(save_path)
                file_url = f"/static/uploads/{filename}"
                upload_success = True
                upload_msg = "上传成功！"

    return render_template("upload.html",
                           upload_msg=upload_msg,
                           upload_success=upload_success,
                           file_url=file_url,
                           filename=filename)


@app.route("/profile", methods=["GET"])
def profile():
    # ⚠️ IDOR漏洞：从URL参数获取user_id，不验证当前登录用户
    user_id = request.args.get("user_id")
    if not user_id:
        return "缺少user_id参数"

    conn = get_db()
    c = conn.cursor()
    # ⚠️ SQL注入漏洞：字符串拼接
    sql = f"SELECT id, username, email, phone, balance FROM users WHERE id = '{user_id}'"
    print(f"[SQL] {sql}")
    try:
        c.execute(sql)
        row = c.fetchone()
        if row:
            profile_user = dict(row)
        else:
            profile_user = None
    except Exception as e:
        print(f"[SQL ERROR] {e}")
        profile_user = None
    conn.close()

    return render_template("profile.html", user=profile_user)


@app.route("/recharge", methods=["POST"])
def recharge():
    # 从表单获取参数
    user_id = request.form.get("user_id")
    amount = request.form.get("amount")

    if not user_id or not amount:
        return "缺少参数"

    # ✅ 修复：金额不能为负数
    try:
        amount_val = float(amount)
        if amount_val <= 0:
            return "充值金额必须为正数"
    except ValueError:
        return "金额格式错误"

    conn = get_db()
    c = conn.cursor()
    # ⚠️ SQL注入漏洞：字符串拼接
    sql = f"UPDATE users SET balance = balance + {amount} WHERE id = '{user_id}'"
    print(f"[SQL] {sql}")
    try:
        c.execute(sql)
        conn.commit()
    except Exception as e:
        print(f"[SQL ERROR] {e}")
    conn.close()

    return redirect(f"/profile?user_id={user_id}")


@app.route("/shop", methods=["GET"])
def shop():
    """商品列表页面"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, price FROM products")
    products = [dict(r) for r in c.fetchall()]
    conn.close()
    return render_template("shop.html", products=products)


@app.route("/cart", methods=["POST"])
def cart():
    """
    ⚠️ 业务逻辑漏洞：商品价格由客户端提交，可被篡改
    Burp拦截后将price改成任意值即可低价购买
    """
    if "username" not in session:
        return redirect("/login")

    product_id = request.form.get("product_id")
    product_name = request.form.get("product_name")
    price = request.form.get("price")  # ⚠️ 客户端提交价格，不可信！
    quantity = request.form.get("quantity", "1")

    # 直接使用客户端提交的价格（漏洞！）
    total = float(price) * int(quantity)

    return render_template("cart.html",
                           product_name=product_name,
                           price=price,
                           quantity=quantity,
                           total=total)


@app.route("/admin", methods=["GET"])
def admin_panel():
    """
    ⚠️ 垂直越权漏洞：未检查当前用户是否为管理员
    普通用户直接访问/admin即可看到管理面板
    """
    if "username" not in session:
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, username, email, balance FROM users")
    users = [dict(r) for r in c.fetchall()]
    conn.close()
    return render_template("admin.html", users=users)


@app.route("/admin/delete-user", methods=["POST"])
def admin_delete_user():
    """
    ⚠️ 垂直越权漏洞：未检查管理员权限
    任何登录用户都可以删除他人账户
    """
    if "username" not in session:
        return redirect("/login")

    user_id = request.form.get("user_id")
    conn = get_db()
    c = conn.cursor()
    # ⚠️ SQL注入漏洞
    sql = f"DELETE FROM users WHERE id = '{user_id}'"
    print(f"[SQL] {sql}")
    c.execute(sql)
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/page", methods=["GET"])
def page():
    """
    ⚠️ 文件包含漏洞：直接拼接用户输入的路径，不做任何过滤
    攻击者可通过 ../ 实现路径穿越，读取任意文件
    """
    name = request.args.get("name", "")
    if not name:
        return "缺少name参数"

    # ⚠️ 漏洞：直接拼接用户输入到路径，未过滤 ../，未使用abspath
    file_path = os.path.join("pages", name)
    page_content = None

    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                page_content = f.read()
        else:
            html_path = file_path + ".html"
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
                    page_content = f.read()
            else:
                page_content = "页面不存在"
    except Exception:
        page_content = "页面不存在"

    # 获取当前用户信息
    username = session.get("username")
    user = None
    if username:
        conn = get_db()
        c = conn.cursor()
        sql = f"SELECT id, username, password, email, phone FROM users WHERE username = '{username}'"
        try:
            c.execute(sql)
            row = c.fetchone()
            if row:
                user = dict(row)
        except:
            pass
        conn.close()

    # 搜索功能
    keyword = request.args.get("keyword", "")
    results = []
    if keyword:
        conn = get_db()
        c = conn.cursor()
        sql = f"SELECT id, username, email, phone FROM users WHERE username LIKE '%{keyword}%' OR email LIKE '%{keyword}%'"
        try:
            c.execute(sql)
            results = [list(r) for r in c.fetchall()]
        except:
            pass
        conn.close()

    return render_template("index.html", user=user, keyword=keyword, results=results, page_content=page_content, page_name=name)


@app.route("/page_fixed", methods=["GET"])
def page_fixed():
    """
    ✅ 修复版：限制页面只能在 pages/ 目录内，过滤路径穿越
    """
    name = request.args.get("name", "")
    if not name:
        return "缺少name参数"

    # ✅ 修复：过滤 ../ 和 /
    if "../" in name or ".." in name:
        return "页面不存在"
    if "/" in name or "\\" in name:
        return "页面不存在"

    file_path = os.path.join("pages", name)
    page_content = None

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            page_content = f.read()
    else:
        html_path = file_path + ".html"
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                page_content = f.read()
        else:
            page_content = "页面不存在"

    return render_template("page_fixed.html", page_content=page_content, page_name=name)


@app.route("/change-password", methods=["POST"])
def change_password():
    """
    ⚠️ 密码修改漏洞：
    - 无需原密码验证
    - 无CSRF Token验证
    - 任何已登录用户可修改任意用户的密码
    """
    if "username" not in session:
        return redirect("/login")

    username = request.form.get("username", "")
    new_password = request.form.get("new_password", "")

    if not username or not new_password:
        return "缺少参数"

    conn = get_db()
    c = conn.cursor()
    # ⚠️ SQL注入漏洞：字符串拼接
    sql = f"UPDATE users SET password = '{new_password}' WHERE username = '{username}'"
    print(f"[SQL] {sql}")
    c.execute(sql)
    conn.commit()
    conn.close()

    return redirect("/profile")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
