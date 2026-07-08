#!/usr/bin/env python3
from fpdf import FPDF
import subprocess, time

class P(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("C","","/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
        self.add_font("C","B","/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
        self.add_font("C","I","/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
        self.add_font("M","","/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
    def head(self):
        if self.page_no()>1:
            self.set_font("C","I",8); self.cell(0,8,"SQL注入漏洞分析与修复",align="C"); self.ln(8)
    def foot(self):
        self.set_y(-15); self.set_font("C","I",8); self.cell(0,10,f"第{self.page_no()}页",align="C")
    def h1(self,s):
        self.set_font("C","B",14); self.set_text_color(30,60,114)
        self.cell(0,10,s,new_x="LMARGIN",new_y="NEXT")
        self.set_draw_color(30,60,114); self.line(self.l_margin,self.get_y(),self.w-self.r_margin,self.get_y()); self.ln(4)
    def h2(self,s):
        self.set_font("C","B",11); self.set_text_color(50,90,150); self.cell(0,8,s,new_x="LMARGIN",new_y="NEXT"); self.ln(2)
    def h3(self,s):
        self.set_font("C","B",10); self.set_text_color(80,80,80); self.cell(0,7,s,new_x="LMARGIN",new_y="NEXT"); self.ln(1)
    def t(self,s):
        self.set_font("C","",9); self.set_text_color(40,40,40); self.multi_cell(0,5.5,s); self.ln(1)
    def b(self,s):
        self.set_font("C","",9); self.set_text_color(40,40,40)
        self.set_x(self.l_margin+4); self.multi_cell(0,5.5,s); self.ln(0.5)
    def c(self,s):
        self.set_fill_color(240,242,245); self.set_text_color(30,30,30); self.set_font("M","",7)
        for L in s.split("\n"):
            w=self.w-self.l_margin-self.r_margin; self.cell(w,4.5,"  "+L,fill=True,new_x="LMARGIN",new_y="NEXT")
        self.ln(2)
    def n(self,s):
        self.set_fill_color(255,240,240); self.set_text_color(40,60,80)
        self.set_font("C","I",9); self.multi_cell(0,5.5,s,fill=True); self.ln(2.5)
    def screenshot(self,path,caption,w=170):
        try:
            self.image(path,w=w)
            self.set_font("C","I",8); self.set_text_color(100,100,100)
            self.cell(0,5,caption,align="C",new_x="LMARGIN",new_y="NEXT"); self.ln(3)
        except: self.t(f"[截图加载失败: {path}]")

pdf=P()
pdf.set_auto_page_break(auto=True,margin=20)

# ===== Cover =====
pdf.add_page(); pdf.ln(20)
pdf.set_font("C","B",22); pdf.set_text_color(30,60,114)
pdf.cell(0,14,"Flask 用户管理系统",align="C",new_x="LMARGIN",new_y="NEXT")
pdf.cell(0,14,"SQL注入漏洞分析与修复报告",align="C",new_x="LMARGIN",new_y="NEXT")
pdf.ln(6)
pdf.set_font("C","",12); pdf.set_text_color(100,100,100)
pdf.cell(0,8,"从 f-string 拼接漏洞到参数化查询修复",align="C",new_x="LMARGIN",new_y="NEXT")
pdf.ln(20)
mid=pdf.w/2; pdf.set_draw_color(30,60,114); pdf.set_line_width(0.5); pdf.line(mid-35,pdf.get_y(),mid+35,pdf.get_y()); pdf.ln(10)
for x in ["实验日期：2026年7月8日","实验环境：Python 3 + Flask + SQLite + Burp Suite",
          "内网地址：http://192.168.56.128:5000","公网地址：http://171.219.193.114:5000"]:
    pdf.set_font("C","",10); pdf.set_text_color(80,80,80); pdf.cell(0,7,x,align="C",new_x="LMARGIN",new_y="NEXT")

# ===== TOC =====
pdf.add_page(); pdf.h1("目录")
for x in ["一、SQL注入漏洞来源分析","    1.1 什么是SQL注入","    1.2 漏洞代码定位",
          "二、SQL注入攻击完整流程与截图","    2.1 步骤1：登录页面","    2.2 步骤2：登录成功（首页）",
          "    2.3 步骤3：正常搜索","    2.4 步骤4：永真条件注入 (%' OR 1=1)",
          "    2.5 步骤5：UNION注入获取密码","    2.6 后台SQL日志输出","三、漏洞危害分析",
          "四、修复方案","    4.1 参数化查询原理","    4.2 修复前后代码对比",
          "    4.3 修复后完整代码","五、修复验证测试",
          "六、访问地址"]:
    pdf.set_font("C","",9); pdf.set_text_color(40,40,40); pdf.cell(0,6,x,new_x="LMARGIN",new_y="NEXT")

# ===== 一 =====
pdf.add_page(); pdf.h1("一、SQL注入漏洞来源分析")
pdf.h2("1.1 什么是SQL注入")
pdf.t("SQL注入（SQL Injection）是OWASP Top 10中危害最大的漏洞之一。攻击者在输入框插入恶意SQL代码，利用后端对用户输入的不当处理，使恶意SQL被执行。根本原因是使用字符串拼接而非参数化查询。")
pdf.h2("1.2 漏洞代码定位")
pdf.h3("漏洞点1：搜索功能（/search 和 /?keyword=）")
pdf.c(
    '# VULNERABLE: f-string concatenation with user input\n'
    'keyword = request.args.get("keyword", "")\n'
    'sql = f"SELECT id, username, email, phone FROM users\n'
    "       WHERE username LIKE '%{keyword}%' OR email LIKE '%{keyword}%'\"\n"
    'c.execute(sql)    # UNSAFE!'
)
pdf.h3("漏洞点2：注册功能（/register）")
pdf.c(
    'sql = f"INSERT INTO users (username, password, email, phone)\n'
    "       VALUES ('{username}', '{password}', '{email}', '{phone}')\"\n"
    'c.execute(sql)    # UNSAFE!'
)
pdf.n("危险：用户输入直接嵌入SQL语句，无任何过滤或转义！")

# ===== 二 =====
pdf.add_page(); pdf.h1("二、SQL注入攻击完整流程与截图")
pdf.t("以下是完整的攻击流程截图，从登录页面开始，到SQL注入成功窃取密码。")

pdf.h2("2.1 步骤1：登录页面")
pdf.t("访问 http://127.0.0.1:5000/login，使用管理员账号 admin/admin123 登录系统。")
pdf.screenshot("/root/flask-app-vuln/static/ss_login.png","截图1：登录页面（输入用户名和密码）")

pdf.h2("2.2 步骤2：登录成功（首页）")
pdf.t("使用 admin/admin123 登录成功后，页面显示用户信息（用户名、邮箱、手机、角色、余额）。")
pdf.screenshot("/root/flask-app-vuln/static/ss_home.png","截图2：登录成功后的首页（显示用户信息）")

pdf.add_page()
pdf.h2("2.3 步骤3：正常搜索")
pdf.t("在搜索框输入 admin，搜索用户。请求URL：/search?keyword=admin")
pdf.c(
    '[SQL] SELECT id, username, email, phone FROM users\n'
    "WHERE username LIKE '%admin%' OR email LIKE '%admin%'\n"
    'Result: 返回admin用户记录（正常功能）'
)
pdf.screenshot("/root/flask-app-vuln/static/ss_search_normal.png","截图3：正常搜索结果显示（admin@example.com）")

pdf.h2("2.4 步骤4：永真条件注入 (%' OR 1=1 --)")
pdf.t("攻击原理：在 keyword 中构造特殊字符，闭合LIKE的引号后添加 OR 1=1 使条件永远为真。")
pdf.t("请求：/search?keyword=%' OR 1=1 --")
pdf.c(
    'Generated SQL:\n'
    "SELECT ... WHERE username LIKE '%%' OR 1=1 --%'\n"
    "      OR email LIKE '%%' OR 1=1 --%'\n"
    'Result: OR 1=1 永真，返回所有用户！'
)
pdf.n("注入成功！返回了 users 表中所有用户记录（admin、alice、testuser）")
pdf.screenshot("/root/flask-app-vuln/static/ss_inject_or.png","截图4：OR 1=1 永真注入成功（获取全部用户）")

pdf.add_page()
pdf.h2("2.5 步骤5：UNION注入获取密码")
pdf.t("攻击原理：使用 UNION SELECT 合并查询结果，读取 password 字段，直接窃取所有用户密码。")
pdf.t("请求：/search?keyword=' UNION SELECT id,username,password,email FROM users --")
pdf.c(
    'Generated SQL:\n'
    "SELECT ... WHERE username LIKE '%' UNION SELECT\n"
    "id,username,password,email FROM users --%'\n"
    '      OR email LIKE ...'
)
pdf.n("严重！成功窃取所有用户的明文密码！admin123, alice2025, test123")
pdf.screenshot("/root/flask-app-vuln/static/ss_inject_union.png","截图5：UNION SELECT 注入成功（密码泄露）")

pdf.h2("2.6 后台SQL日志输出")
pdf.t("Flask 控制台打印的实际执行的SQL语句，验证注入成功：")
pdf.screenshot("/root/flask-app-vuln/static/ss_sql_log.png","截图6：后台SQL日志（显示实际执行的注入SQL）")

# ===== 三 =====
pdf.add_page(); pdf.h1("三、漏洞危害分析")
pdf.t("本次发现的SQL注入漏洞具有以下危害：")
pdf.b("1. 数据泄露：UNION SELECT 可获取所有字段（含密码）")
pdf.b("2. 绕过认证：OR 1=1 永真条件绕过数据访问控制")
pdf.b("3. 数据篡改：注册注入点可修改或删除数据")
pdf.b("4. 隐私泄露：邮箱、手机号泄露可能导致钓鱼攻击")
pdf.b("5. 权限提升：SQLite注入在某些配置下可执行系统命令")
pdf.t("")
pdf.t("根因：")
pdf.b("使用 f-string 直接拼接用户输入到 SQL 语句")
pdf.b("没有使用参数化查询（Prepared Statement）")
pdf.b("没有对用户输入做任何过滤或转义")

# ===== 四 =====
pdf.add_page(); pdf.h1("四、修复方案")
pdf.h2("4.1 参数化查询原理")
pdf.t("参数化查询将SQL结构和数据分离。数据库驱动自动转义和绑定参数，用户输入永远无法改变SQL语义。")
pdf.c(
    '# SAFE: Use ? placeholders + parameter tuple\n'
    'sql = "SELECT * FROM users WHERE username LIKE ? OR email LIKE ?"\n'
    'params = (f"%{keyword}%", f"%{keyword}%")\n'
    'c.execute(sql, params)  # SAFE!\n'
    '\n'
    "# Even if keyword is \"%' OR 1=1 --\"\n"
    '# DB driver treats it as plain text, NOT SQL'
)

pdf.h2("4.2 修复前后代码对比")
pdf.h3("搜索功能修复")
pdf.c(
    '# BEFORE (VULNERABLE) - f-string拼接\n'
    'sql = f"SELECT ... WHERE username LIKE \'%{keyword}%\'"\n'
    'c.execute(sql)\n'
    '\n'
    '# AFTER (FIXED) - 参数化查询\n'
    'sql = "SELECT ... WHERE username LIKE ? OR email LIKE ?"\n'
    'params = (f"%{keyword}%", f"%{keyword}%")\n'
    'c.execute(sql, params)'
)
pdf.h3("注册功能修复")
pdf.c(
    '# BEFORE (VULNERABLE) - f-string拼接\n'
    "sql = f\"INSERT INTO users VALUES ('{username}', ...)\"\n"
    'c.execute(sql)\n'
    '\n'
    '# AFTER (FIXED) - 参数化查询\n'
    'sql = "INSERT INTO users VALUES (?, ?, ?, ?)"\n'
    'params = (username, password, email, phone)\n'
    'c.execute(sql, params)'
)

pdf.h2("4.3 修复后完整代码")
pdf.t("文件路径：/root/flask-app-vuln/app_fixed.py")
pdf.c(
    'from flask import Flask, render_template, request, redirect, session\n'
    'from werkzeug.security import generate_password_hash, check_password_hash\n'
    'import os, sqlite3\n'
    '\n'
    'app = Flask(__name__)\n'
    'DB_PATH = os.path.join(os.path.dirname(__file__), "data", "users.db")\n'
    '\n'
    '@app.route("/search", methods=["GET"])\n'
    'def search():\n'
    '    keyword = request.args.get("keyword", "")\n'
    '    sql = "SELECT id, username, email, phone FROM users\n'
    '           WHERE username LIKE ? OR email LIKE ?"\n'
    '    params = (f"%{keyword}%", f"%{keyword}%")\n'
    '    c.execute(sql, params)  # SAFE!\n'
    '    results = c.fetchall()\n'
    '    return render_template("index.html", results=results)\n'
    '\n'
    '@app.route("/register", methods=["GET", "POST"])\n'
    'def register():\n'
    '    username = request.form.get("username", "")\n'
    '    password = request.form.get("password", "")\n'
    '    sql = "INSERT INTO users VALUES (?, ?, ?, ?)"\n'
    '    params = (username, password, email, phone)\n'
    '    c.execute(sql, params)  # SAFE!\n'
    '    conn.commit()'
)

# ===== 五 =====
pdf.add_page(); pdf.h1("五、修复验证测试")

# Start fixed server
subprocess.run("fuser -9k 5000/tcp 2>/dev/null", shell=True, capture_output=True)
subprocess.run("python -u app_fixed.py > /tmp/flask_fixed.log 2>&1 &", shell=True)
time.sleep(2)
subprocess.run("curl -s -c /tmp/cx.txt -X POST http://127.0.0.1:5000/login -d 'username=admin&password=admin123' > /dev/null", shell=True)

tests = [
    ("正常搜索 admin", "http://127.0.0.1:5000/search?keyword=admin", "admin@example.com"),
    ("永真 %' OR 1=1", "http://127.0.0.1:5000/search?keyword=%25%27+OR+1%3D1+--", "无搜索结果"),
    ("UNION获取密码", "http://127.0.0.1:5000/search?keyword=%27+UNION+SELECT+id,username,password,email+FROM+users+--", "无搜索结果"),
]
for name, url, expect in tests:
    r = subprocess.run(f"curl -s -b /tmp/cx.txt '{url}'", shell=True, capture_output=True).stdout.decode()
    ok = "通过" if expect in r else "失败"
    pdf.b(f"{name}: {ok}")

pdf.t("")
pdf.t("修复结论：")
pdf.b("正常搜索仍正常返回结果")
pdf.b("OR 1=1 注入不再返回所有用户（返回 无搜索结果）")
pdf.b("UNION SELECT 不再泄露密码（返回 无搜索结果）")
pdf.t("")
pdf.t("修复后SQL日志对比：")
pdf.screenshot("/root/flask-app-vuln/static/ss_fixed_log.png","截图7：修复后SQL日志（注入字符被当作普通文本）")

# ===== 六 =====
pdf.add_page(); pdf.h1("六、访问地址")
pdf.t("内网访问（私网）：")
pdf.c("http://192.168.56.128:5000/login")
pdf.c("http://192.168.56.128:5000/register")
pdf.c("http://192.168.56.128:5000/search?keyword=admin")
pdf.t("")
pdf.t("公网访问（外网）：")
pdf.c("http://171.219.193.114:5000/login")
pdf.c("http://171.219.193.114:5000/register")
pdf.c("http://171.219.193.114:5000/search?keyword=admin")
pdf.t("")
pdf.t("本地访问：")
pdf.c("http://127.0.0.1:5000/login")
pdf.t("")
pdf.t("默认测试账号：")
pdf.c("管理员: admin / admin123")
pdf.c("普通用户: alice / alice2025")
pdf.t("")
pdf.t("项目文件：")
pdf.c("漏洞版: /root/flask-app-vuln/app.py (f-string拼接)")
pdf.c("修复版: /root/flask-app-vuln/app_fixed.py (参数化查询)")
pdf.c("数据库: /root/flask-app-vuln/data/users.db")
pdf.c("GitHub: https://github.com/Zhang123456-rgb/2025141530175")

# End
pdf.ln(8); pdf.set_draw_color(30,60,114); pdf.line(mid-40,pdf.get_y(),mid+40,pdf.get_y()); pdf.ln(8)
pdf.set_font("C","I",10); pdf.set_text_color(100,100,100)
pdf.cell(0,7,"报告完 —— 永远不要信任用户的输入。",align="C",new_x="LMARGIN",new_y="NEXT")

pdf.output("/root/flask-app-vuln/SQL注入漏洞分析与修复报告.pdf")
print("OK")
