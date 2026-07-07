#!/usr/bin/env python3
"""生成 Flask 安全漏洞修复报告 PDF"""

from fpdf import FPDF
import textwrap

class ReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        # 注册中文字体
        self.add_font("CN", "", "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
        self.add_font("CN", "B", "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
        self.add_font("CN", "I", "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
        self.add_font("CNMono", "", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")

    def header(self):
        if self.page_no() > 1:
            self.set_font("CN", "I", 8)
            self.cell(0, 8, "Flask 登录系统 - 安全漏洞修复报告", align="C")
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("CN", "I", 8)
        self.cell(0, 10, f"第 {self.page_no()} 页", align="C")

    def title_section(self, title):
        self.set_font("CN", "B", 16)
        self.set_text_color(30, 60, 114)
        self.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 60, 114)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def sub_title(self, title):
        self.set_font("CN", "B", 13)
        self.set_text_color(50, 90, 150)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def sub_sub_title(self, title):
        self.set_font("CN", "B", 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("CN", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def code_block(self, code, lang=""):
        """Render code in monospace with light gray background"""
        self.set_fill_color(240, 242, 245)
        self.set_text_color(30, 30, 30)
        self.set_font("CNMono", "", 8)
        for line in code.split("\n"):
            # Calculate approximate width
            w = self.w - self.l_margin - self.r_margin
            self.cell(w, 5, "  " + line, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def diff_block(self, title_before, code_before, title_after, code_after):
        """Show before/after side by side in two columns"""
        col_w = (self.w - self.l_margin - self.r_margin - 4) / 2

        # Headers
        self.set_font("CN", "B", 9)
        self.set_fill_color(200, 60, 60)
        self.set_text_color(255, 255, 255)
        self.cell(col_w, 7, f"  {title_before}", fill=True)
        self.cell(4, 7, "")
        self.set_fill_color(60, 160, 60)
        self.cell(col_w, 7, f"  {title_after}", fill=True)
        self.ln(7)

        # Code
        before_lines = code_before.split("\n")
        after_lines = code_after.split("\n")
        max_lines = max(len(before_lines), len(after_lines))

        self.set_font("CNMono", "", 7.5)
        for i in range(max_lines):
            b_line = before_lines[i] if i < len(before_lines) else ""
            a_line = after_lines[i] if i < len(after_lines) else ""
            self.set_fill_color(255, 235, 235)
            self.set_text_color(180, 40, 40)
            self.cell(col_w, 4.5, "  " + b_line, fill=True)
            self.cell(4, 4.5, "")
            self.set_fill_color(235, 255, 235)
            self.set_text_color(30, 130, 30)
            self.cell(col_w, 4.5, "  " + a_line, fill=True)
            self.ln(4.5)
        self.ln(3)

    def note_box(self, text, color=(230, 245, 255)):
        self.set_fill_color(*color)
        self.set_text_color(40, 60, 80)
        self.set_font("CN", "I", 9)
        self.multi_cell(0, 6, text, fill=True)
        self.ln(3)


def build_pdf():
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ============ COVER ============
    pdf.set_font("CN", "B", 26)
    pdf.set_text_color(30, 60, 114)
    pdf.ln(40)
    pdf.cell(0, 15, "Flask 用户管理系统", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 15, "安全漏洞修复报告", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("CN", "", 13)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "三处安全漏洞分析与修复方案", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("CN", "", 10)
    pdf.cell(0, 8, "Python Flask  |  Werkzeug  |  Session 安全", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_draw_color(30, 60, 114)
    pdf.set_line_width(0.5)
    mid = pdf.w / 2
    pdf.line(mid - 30, pdf.get_y(), mid + 30, pdf.get_y())
    pdf.ln(15)
    pdf.set_font("CN", "", 10)
    pdf.cell(0, 8, "2026-07-07", align="C", new_x="LMARGIN", new_y="NEXT")

    # ============ TABLE OF CONTENTS ============
    pdf.add_page()
    pdf.title_section("目  录")
    toc = [
        ("一、项目概述", ""),
        ("二、初始源代码（三处漏洞全部存在）", ""),
        ("    2.1  app.py", ""),
        ("    2.2  templates/index.html", ""),
        ("    2.3  templates/login.html", ""),
        ("    2.4  templates/base.html", ""),
        ("三、三处漏洞的代码修改对比", ""),
        ("    3.1  漏洞一：密码明文存储 + 明文比对", ""),
        ("    3.2  漏洞二：弱 Secret Key", ""),
        ("    3.3  漏洞三：HTML注释泄露管理员账号", ""),
        ("四、每处漏洞修复后的完整源代码", ""),
        ("    4.1  修复漏洞一之后", ""),
        ("    4.2  修复漏洞二之后", ""),
        ("    4.3  修复漏洞三之后", ""),
        ("五、最终完整源代码（全部修复）", ""),
        ("    5.1  app.py", ""),
        ("    5.2  templates/index.html", ""),
        ("    5.3  templates/login.html", ""),
        ("    5.4  templates/base.html", ""),
        ("    5.5  static/css/style.css", ""),
        ("六、修改行号对照总表", ""),
    ]
    for title, _ in toc:
        pdf.set_font("CN", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 7, f"  {title}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # ============ 一、项目概述 ============
    pdf.add_page()
    pdf.title_section("一、项目概述")
    pdf.body_text(
        "本项目是一个简易用户信息管理平台的登录功能，使用 Python Flask 框架构建。"
        "项目包含 5 个文件：app.py（主应用）、templates/base.html（基础模板）、"
        "templates/login.html（登录页）、templates/index.html（首页）、"
        "static/css/style.css（样式文件）。"
    )
    pdf.body_text("初始版本故意留有 3 个安全漏洞用于教学演示，以下逐一展示并修复。")
    pdf.body_text("漏洞列表：")
    pdf.body_text("  - 漏洞一：密码以明文形式存储在字典中，使用 == 直接比较，登录后密码原文暴露在页面上")
    pdf.body_text("  - 漏洞二：Secret Key 硬编码为 \"dev-key-2025\"，可被 flask-unsign 解签伪造 session")
    pdf.body_text("  - 漏洞三：login.html 中 HTML 注释直接泄露管理员账号密码")

    # ============ 二、初始源代码 ============
    pdf.add_page()
    pdf.title_section("二、初始源代码（三处漏洞全部存在）")

    pdf.sub_title("2.1  app.py（漏洞版）")
    pdf.code_block(
        'from flask import Flask, render_template, request, redirect, session\n'
        '\n'
        'app = Flask(__name__)\n'
        'app.secret_key = "dev-key-2025"\n'
        '\n'
        '# 明文密码用户数据库（故意不加密，用于教学演示）\n'
        'USERS = {\n'
        '    "admin": {\n'
        '        "username": "admin",\n'
        '        "password": "admin123",\n'
        '        "role": "admin",\n'
        '        "email": "admin@example.com",\n'
        '        "phone": "13800138000",\n'
        '        "balance": 99999\n'
        '    },\n'
        '    "alice": {\n'
        '        "username": "alice",\n'
        '        "password": "alice2025",\n'
        '        "role": "user",\n'
        '        "email": "alice@example.com",\n'
        '        "phone": "13900139001",\n'
        '        "balance": 100\n'
        '    }\n'
        '}\n'
        '\n'
        '@app.route("/")\n'
        'def index():\n'
        '    username = session.get("username")\n'
        '    user = None\n'
        '    if username and username in USERS:\n'
        '        user = USERS[username]\n'
        '    return render_template("index.html", user=user)\n'
        '\n'
        '@app.route("/login", methods=["GET", "POST"])\n'
        'def login():\n'
        '    error = None\n'
        '    if request.method == "POST":\n'
        '        username = request.form.get("username", "")\n'
        '        password = request.form.get("password", "")\n'
        '        # 直接明文比对密码（故意不加密）\n'
        '        if username in USERS and USERS[username]["password"] == password:\n'
        '            session["username"] = username\n'
        '            user = USERS[username]\n'
        '            return render_template("index.html", user=user)\n'
        '        else:\n'
        '            error = "用户名或密码错误！"\n'
        '    return render_template("login.html", error=error)\n'
        '\n'
        '@app.route("/logout")\n'
        'def logout():\n'
        '    session.clear()\n'
        '    return redirect("/")\n'
        '\n'
        'if __name__ == "__main__":\n'
        '    app.run(debug=True, host="0.0.0.0", port=5000)'
    )

    pdf.sub_title("2.2  templates/index.html（漏洞版）")
    pdf.code_block(
        '{% extends "base.html" %}\n'
        '{% block content %}\n'
        '<div class="card">\n'
        '    {% if user %}\n'
        '        <h2>欢迎回来，{{ user.username }}！</h2>\n'
        '        <h3>用户信息</h3>\n'
        '        <ul class="user-info">\n'
        '            <li><strong>用户名：</strong>{{ user.username }}</li>\n'
        '            <li><strong>密码：</strong>{{ user.password }}</li>\n'
        '            <li><strong>邮箱：</strong>{{ user.email }}</li>\n'
        '            <li><strong>手机：</strong>{{ user.phone }}</li>\n'
        '            <li><strong>角色：</strong>{{ user.role }}</li>\n'
        '            <li><strong>余额：</strong>{{ user.balance }}</li>\n'
        '        </ul>\n'
        '        <a href="/logout" class="btn btn-logout">退出登录</a>\n'
        '    {% else %}\n'
        '        <h2>请先登录</h2>\n'
        '        <p>您尚未登录，请点击下方按钮登录系统。</p>\n'
        '        <a href="/login" class="btn">前往登录</a>\n'
        '    {% endif %}\n'
        '</div>\n'
        '{% endblock %}'
    )

    pdf.sub_title("2.3  templates/login.html（漏洞版）")
    pdf.code_block(
        '<!-- 调试信息 - 默认管理员账号 用户名: admin 密码: admin123 -->\n'
        '{% extends "base.html" %}\n'
        '{% block content %}\n'
        '<div class="card">\n'
        '    <h2>用户登录</h2>\n'
        '    ...\n'
        '</div>\n'
        '{% endblock %}'
    )

    pdf.sub_title("2.4  templates/base.html（未改动）")
    pdf.code_block(
        '<!DOCTYPE html>\n'
        '<html lang="zh-CN">\n'
        '<head>\n'
        '    <meta charset="UTF-8">\n'
        '    <title>用户管理系统</title>\n'
        '    <link rel="stylesheet" href="/static/css/style.css">\n'
        '</head>\n'
        '<body>\n'
        '    <nav class="navbar">\n'
        '        <div class="nav-left">\n'
        '            <span class="brand">用户管理系统</span>\n'
        '        </div>\n'
        '        <div class="nav-right">\n'
        '            {% if session.get(\'username\') %}\n'
        '                <span class="nav-welcome">欢迎，{{ session[\'username\'] }}</span>\n'
        '                <a href="/logout" class="nav-link">退出</a>\n'
        '            {% else %}\n'
        '                <a href="/login" class="nav-link">登录</a>\n'
        '            {% endif %}\n'
        '        </div>\n'
        '    </nav>\n'
        '    <main class="container">\n'
        '        {% block content %}{% endblock %}\n'
        '    </main>\n'
        '</body>\n'
        '</html>'
    )

    # ============ 三、修改对比 ============
    pdf.add_page()
    pdf.title_section("三、三处漏洞的代码修改对比")

    # --- 漏洞一 ---
    pdf.sub_title("3.1  漏洞一：密码明文存储 + 明文比对")
    pdf.sub_sub_title("涉及文件：app.py + templates/index.html")

    pdf.note_box("问题说明：USERS 字典中密码以明文存储（admin123 / alice2025），"
                 "登录时用 == 直接比较字符串，登录后首页直接输出 {{ user.password }} 暴露密码原文。",
                 color=(255, 235, 235))

    pdf.body_text("修改一：app.py - 新增安全库导入")
    pdf.diff_block(
        "修改前",
        'from flask import Flask, render_template, request, redirect, session',
        "修改后",
        'from flask import Flask, render_template, request, redirect, session\nfrom werkzeug.security import generate_password_hash, check_password_hash'
    )

    pdf.body_text("修改二：app.py - USERS 字典密码哈希化")
    pdf.diff_block(
        "修改前",
        '"password": "admin123",\n"password": "alice2025",',
        "修改后",
        '"password": generate_password_hash("admin123"),\n"password": generate_password_hash("alice2025"),'
    )

    pdf.body_text("修改三：app.py - 登录比对方式")
    pdf.diff_block(
        "修改前",
        '# 直接明文比对密码（故意不加密）\nif username in USERS and USERS[username]["password"] == password:',
        "修改后",
        '# 使用哈希比对密码，不再直接 == 比较\nif username in USERS and check_password_hash(USERS[username]["password"], password):'
    )

    pdf.body_text("修改四：index.html - 页面密码展示")
    pdf.diff_block(
        "修改前",
        '<li><strong>密码：</strong>{{ user.password }}</li>',
        "修改后",
        '<li><strong>密码：</strong>********（已加密保护）</li>'
    )

    # --- 漏洞二 ---
    pdf.add_page()
    pdf.sub_title("3.2  漏洞二：弱 Secret Key（Session 伪造风险）")
    pdf.sub_sub_title("涉及文件：app.py")

    pdf.note_box("问题说明：Secret Key 硬编码为 \"dev-key-2025\"，"
                 "这是一个公开的弱密钥。攻击者可使用 flask-unsign 工具解签 session cookie，"
                 "篡改其中 username 字段后重新签名，从而伪造任意用户身份登录系统。",
                 color=(255, 235, 235))

    pdf.body_text("修改一：app.py - 新增 os 模块导入")
    pdf.diff_block(
        "修改前",
        'from flask import Flask, render_template, request, redirect, session',
        "修改后",
        'from flask import Flask, render_template, request, redirect, session\nfrom werkzeug.security import generate_password_hash, check_password_hash\nimport os'
    )

    pdf.body_text("修改二：app.py - Secret Key 改为随机生成")
    pdf.diff_block(
        "修改前",
        'app.secret_key = "dev-key-2025"',
        "修改后",
        'app.secret_key = os.urandom(24).hex()  # 随机生成密钥，防止 session 伪造'
    )

    # --- 漏洞三 ---
    pdf.sub_title("3.3  漏洞三：HTML 注释泄露管理员账号")
    pdf.sub_sub_title("涉及文件：templates/login.html")

    pdf.note_box("问题说明：login.html 第 1 行 HTML 注释中直接写明了默认管理员的用户名和密码，"
                 "任何用户通过查看页面源代码（F12 或右键查看源代码）即可获取登录凭证。",
                 color=(255, 235, 235))

    pdf.body_text("login.html - 注释内容修改")
    pdf.diff_block(
        "修改前",
        '<!-- 调试信息 - 默认管理员账号 用户名: admin 密码: admin123 -->',
        "修改后",
        '<!-- 调试信息 - 请联系管理员获取账号 -->'
    )

    # ============ 四、每处漏洞修复后的完整源代码 ============
    pdf.add_page()
    pdf.title_section("四、每处漏洞修复后的完整源代码")

    pdf.sub_title("4.1  修复漏洞一之后（漏洞二、三仍存在）")
    pdf.note_box("说明：此处仅修复了漏洞一（密码哈希化），"
                 "app.py 中 secret_key 仍为 \"dev-key-2025\"（漏洞二），"
                 "login.html 仍包含泄露账号的注释（漏洞三）。",
                 color=(230, 245, 255))

    pdf.code_block(
        'from flask import Flask, render_template, request, redirect, session\n'
        'from werkzeug.security import generate_password_hash, check_password_hash  # ← 新增\n'
        '\n'
        'app = Flask(__name__)\n'
        'app.secret_key = "dev-key-2025"       # ← 漏洞二还未修复\n'
        '\n'
        '# 用户数据库（密码经哈希处理，不再存储明文）\n'
        'USERS = {\n'
        '    "admin": {\n'
        '        "username": "admin",\n'
        '        "password": generate_password_hash("admin123"),   # ← 已修复\n'
        '        "role": "admin",\n'
        '        "email": "admin@example.com",\n'
        '        "phone": "13800138000",\n'
        '        "balance": 99999\n'
        '    },\n'
        '    "alice": {\n'
        '        "username": "alice",\n'
        '        "password": generate_password_hash("alice2025"),  # ← 已修复\n'
        '        ...\n'
        '    }\n'
        '}\n'
        '...\n'
        '        # 使用哈希比对密码，不再直接 == 比较\n'
        '        if username in USERS and check_password_hash(USERS[username]["password"], password):'
    )

    pdf.sub_title("4.2  修复漏洞二之后（漏洞三仍存在）")
    pdf.note_box("说明：漏洞一和漏洞二已修复。app.py 中密码已哈希、"
                 "secret_key 已随机生成，但 login.html 仍包含泄露账号的注释。",
                 color=(230, 245, 255))

    pdf.code_block(
        'from flask import Flask, render_template, request, redirect, session\n'
        'from werkzeug.security import generate_password_hash, check_password_hash\n'
        'import os                                                               # ← 新增\n'
        '\n'
        'app = Flask(__name__)\n'
        'app.secret_key = os.urandom(24).hex()  # 随机生成密钥，防止 session 伪造 # ← 已修复\n'
        '\n'
        '# 用户数据库（密码经哈希处理，不再存储明文）\n'
        'USERS = {\n'
        '    "admin": {\n'
        '        "username": "admin",\n'
        '        "password": generate_password_hash("admin123"),\n'
        '        ...\n'
        '    },\n'
        '    "alice": {\n'
        '        "username": "alice",\n'
        '        "password": generate_password_hash("alice2025"),\n'
        '        ...\n'
        '    }\n'
        '}\n'
        '...\n'
        '# login.html 中仍是：\n'
        '<!-- 调试信息 - 默认管理员账号 用户名: admin 密码: admin123 -->  # ← 漏洞三未修复'
    )

    pdf.sub_title("4.3  修复漏洞三之后（全部修复完成）")
    pdf.note_box("说明：login.html 注释中的敏感信息已删除，三处漏洞全部修复完毕。",
                 color=(235, 255, 235))

    pdf.code_block(
        '<!-- 调试信息 - 请联系管理员获取账号 -->  # ← 已修复\n'
        '{% extends "base.html" %}\n'
        '{% block content %}\n'
        '<div class="card">\n'
        '    ...\n'
        '</div>\n'
        '{% endblock %}'
    )

    # ============ 五、最终完整源代码 ============
    pdf.add_page()
    pdf.title_section("五、最终完整源代码（全部修复）")

    pdf.sub_title("5.1  app.py（最终版）")
    pdf.code_block(
        'from flask import Flask, render_template, request, redirect, session\n'
        'from werkzeug.security import generate_password_hash, check_password_hash\n'
        'import os\n'
        '\n'
        'app = Flask(__name__)\n'
        'app.secret_key = os.urandom(24).hex()  # 随机生成密钥\n'
        '\n'
        '# 用户数据库（密码经哈希处理，不再存储明文）\n'
        'USERS = {\n'
        '    "admin": {\n'
        '        "username": "admin",\n'
        '        "password": generate_password_hash("admin123"),\n'
        '        "role": "admin",\n'
        '        "email": "admin@example.com",\n'
        '        "phone": "13800138000",\n'
        '        "balance": 99999\n'
        '    },\n'
        '    "alice": {\n'
        '        "username": "alice",\n'
        '        "password": generate_password_hash("alice2025"),\n'
        '        "role": "user",\n'
        '        "email": "alice@example.com",\n'
        '        "phone": "13900139001",\n'
        '        "balance": 100\n'
        '    }\n'
        '}\n'
        '\n'
        '\n'
        '@app.route("/")\n'
        'def index():\n'
        '    username = session.get("username")\n'
        '    user = None\n'
        '    if username and username in USERS:\n'
        '        user = USERS[username]\n'
        '    return render_template("index.html", user=user)\n'
        '\n'
        '\n'
        '@app.route("/login", methods=["GET", "POST"])\n'
        'def login():\n'
        '    error = None\n'
        '    if request.method == "POST":\n'
        '        username = request.form.get("username", "")\n'
        '        password = request.form.get("password", "")\n'
        '        if username in USERS and check_password_hash(USERS[username]["password"], password):\n'
        '            session["username"] = username\n'
        '            user = USERS[username]\n'
        '            return render_template("index.html", user=user)\n'
        '        else:\n'
        '            error = "用户名或密码错误！"\n'
        '    return render_template("login.html", error=error)\n'
        '\n'
        '\n'
        '@app.route("/logout")\n'
        'def logout():\n'
        '    session.clear()\n'
        '    return redirect("/")\n'
        '\n'
        '\n'
        'if __name__ == "__main__":\n'
        '    app.run(debug=True, host="0.0.0.0", port=5000)'
    )

    pdf.sub_title("5.2  templates/index.html（最终版）")
    pdf.code_block(
        '{% extends "base.html" %}\n'
        '{% block content %}\n'
        '<div class="card">\n'
        '    {% if user %}\n'
        '        <h2>欢迎回来，{{ user.username }}！</h2>\n'
        '        <h3>用户信息</h3>\n'
        '        <ul class="user-info">\n'
        '            <li><strong>用户名：</strong>{{ user.username }}</li>\n'
        '            <li><strong>密码：</strong>********（已加密保护）</li>\n'
        '            <li><strong>邮箱：</strong>{{ user.email }}</li>\n'
        '            <li><strong>手机：</strong>{{ user.phone }}</li>\n'
        '            <li><strong>角色：</strong>{{ user.role }}</li>\n'
        '            <li><strong>余额：</strong>{{ user.balance }}</li>\n'
        '        </ul>\n'
        '        <a href="/logout" class="btn btn-logout">退出登录</a>\n'
        '    {% else %}\n'
        '        <h2>请先登录</h2>\n'
        '        <p>您尚未登录，请点击下方按钮登录系统。</p>\n'
        '        <a href="/login" class="btn">前往登录</a>\n'
        '    {% endif %}\n'
        '</div>\n'
        '{% endblock %}'
    )

    pdf.sub_title("5.3  templates/login.html（最终版）")
    pdf.code_block(
        '<!-- 调试信息 - 请联系管理员获取账号 -->\n'
        '{% extends "base.html" %}\n'
        '{% block content %}\n'
        '<div class="card">\n'
        '    <h2>用户登录</h2>\n'
        '    <form method="post" action="/login" class="login-form">\n'
        '        <div class="form-group">\n'
        '            <label for="username">用户名</label>\n'
        '            <input type="text" id="username" name="username" placeholder="请输入用户名" required>\n'
        '        </div>\n'
        '        <div class="form-group">\n'
        '            <label for="password">密码</label>\n'
        '            <input type="password" id="password" name="password" placeholder="请输入密码" required>\n'
        '        </div>\n'
        '        {% if error %}\n'
        '            <p class="error-msg">{{ error }}</p>\n'
        '        {% endif %}\n'
        '        <button type="submit" class="btn">登录</button>\n'
        '    </form>\n'
        '</div>\n'
        '{% endblock %}'
    )

    pdf.sub_title("5.4  templates/base.html（最终版，未改动）")
    pdf.code_block(
        '<!DOCTYPE html>\n'
        '<html lang="zh-CN">\n'
        '<head>\n'
        '    <meta charset="UTF-8">\n'
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '    <title>用户管理系统</title>\n'
        '    <link rel="stylesheet" href="/static/css/style.css">\n'
        '</head>\n'
        '<body>\n'
        '    <nav class="navbar">\n'
        '        <div class="nav-left">\n'
        '            <span class="brand">用户管理系统</span>\n'
        '        </div>\n'
        '        <div class="nav-right">\n'
        '            {% if session.get(\'username\') %}\n'
        '                <span class="nav-welcome">欢迎，{{ session[\'username\'] }}</span>\n'
        '                <a href="/logout" class="nav-link">退出</a>\n'
        '            {% else %}\n'
        '                <a href="/login" class="nav-link">登录</a>\n'
        '            {% endif %}\n'
        '        </div>\n'
        '    </nav>\n'
        '    <main class="container">\n'
        '        {% block content %}{% endblock %}\n'
        '    </main>\n'
        '</body>\n'
        '</html>'
    )

    pdf.sub_title("5.5  static/css/style.css（最终版，未改动）")
    pdf.code_block(
        '/* 全局 reset */\n'
        '* { margin: 0; padding: 0; box-sizing: border-box; }\n'
        'body { font-family: ...; background-color: #f5f7fa; ... }\n'
        '\n'
        '/* 导航栏 - 蓝色渐变背景 */\n'
        '.navbar { background: linear-gradient(135deg, #667eea, #764ba2); ... }\n'
        '\n'
        '/* 卡片 - 白色背景，圆角，阴影 */\n'
        '.card { background: #fff; border-radius: 12px; box-shadow: 0 4px 20px ...; }\n'
        '\n'
        '/* 表单 - 输入框边框和内边距 */\n'
        '.form-group input { border: 1px solid #ddd; padding: 10px 14px; ... }\n'
        '\n'
        '/* 按钮 - 蓝色渐变背景 */\n'
        '.btn { background: linear-gradient(135deg, #667eea, #764ba2); ... }'
    )

    # ============ 六、修改行号对照总表 ============
    pdf.add_page()
    pdf.title_section("六、修改行号对照总表")

    pdf.set_font("CN", "B", 10)
    pdf.set_fill_color(30, 60, 114)
    pdf.set_text_color(255, 255, 255)
    col_w = (pdf.w - pdf.l_margin - pdf.r_margin) / 6
    headers = ["漏洞", "文件", "行号", "修改前", "修改后", "风险等级"]
    for h in headers:
        pdf.cell(col_w, 8, h, border=1, align="C", fill=True)
    pdf.ln()

    rows = [
        ("漏洞一", "app.py", "第2行", "无安全导入", "加 werkzeug.security", "高"),
        ("漏洞一", "app.py", "第10/20行", '"admin123"明文', 'generate_password_hash()', "高"),
        ("漏洞一", "app.py", "第43行", "== 直接比", "check_password_hash()", "高"),
        ("漏洞一", "index.html", "第9行", "{{ user.password }}", "******掩码", "中"),
        ("漏洞二", "app.py", "第3行", "无 os 导入", "加 import os", "高"),
        ("漏洞二", "app.py", "第4行", '"dev-key-2025"', "os.urandom(24)", "高"),
        ("漏洞三", "login.html", "第1行", 'admin/admin123', "请联系管理员", "高"),
    ]

    pdf.set_font("CN", "", 9)
    for row in rows:
        pdf.set_text_color(40, 40, 40)
        for i, cell in enumerate(row):
            pdf.cell(col_w, 7, cell, border=1, align="C")
        pdf.ln()

    pdf.ln(10)
    pdf.sub_sub_title("修复后验证结果")
    pdf.body_text('  - admin/admin123 登录成功，首页密码显示为 【已加密保护】')
    pdf.body_text('  - admin/错误密码 登录失败，提示“用户名或密码错误！”')
    pdf.body_text('  - 未登录用户看到“请先登录”提示')
    pdf.body_text('  - Session 密钥每次启动随机生成，flask-unsign 无法伪造')
    pdf.body_text('  - 查看 login.html 页面源代码，无法获取管理员账号信息')

    # Save
    pdf.output("/root/flask-app-vuln/Flask_安全漏洞修复报告.pdf")
    print("PDF 生成成功！")
    print("路径: /root/flask-app-vuln/Flask_安全漏洞修复报告.pdf")


if __name__ == "__main__":
    build_pdf()
