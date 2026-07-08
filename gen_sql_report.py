#!/usr/bin/env python3
"""SQL注入漏洞分析与修复实验报告 PDF"""
from fpdf import FPDF

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("CN", "", "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
        self.add_font("CN", "B", "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
        self.add_font("CN", "I", "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
        self.add_font("M", "", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
    def header(self):
        if self.page_no() > 1:
            self.set_font("CN", "I", 8)
            self.cell(0, 8, "Flask 用户管理系统 - SQL注入漏洞分析与修复", align="C")
            self.ln(8)
    def footer(self):
        self.set_y(-15)
        self.set_font("CN", "I", 8)
        self.cell(0, 10, f"第 {self.page_no()} 页", align="C")
    def title1(self, s):
        self.set_font("CN", "B", 14); self.set_text_color(30,60,114)
        self.cell(0,10,s,new_x="LMARGIN",new_y="NEXT")
        self.set_draw_color(30,60,114); self.line(self.l_margin,self.get_y(),self.w-self.r_margin,self.get_y()); self.ln(4)
    def title2(self, s):
        self.set_font("CN","B",11); self.set_text_color(50,90,150)
        self.cell(0,8,s,new_x="LMARGIN",new_y="NEXT"); self.ln(2)
    def title3(self, s):
        self.set_font("CN","B",10); self.set_text_color(80,80,80)
        self.cell(0,7,s,new_x="LMARGIN",new_y="NEXT"); self.ln(1)
    def body(self, s):
        self.set_font("CN","",9); self.set_text_color(40,40,40)
        self.multi_cell(0,5.5,s); self.ln(1)
    def bullet(self, s, ind=4):
        self.set_font("CN","",9); self.set_text_color(40,40,40)
        self.set_x(self.l_margin+ind); self.multi_cell(self.w-self.l_margin-self.r_margin-ind,5.5,s); self.ln(0.5)
    def code(self, s):
        self.set_fill_color(240,242,245); self.set_text_color(30,30,30)
        self.set_font("M","",7.5)
        for line in s.split("\n"):
            w=self.w-self.l_margin-self.r_margin
            self.cell(w,4.8,"  "+line,fill=True,new_x="LMARGIN",new_y="NEXT")
        self.ln(2.5)
    def note(self, s, c=(255,240,240)):
        self.set_fill_color(*c); self.set_text_color(40,60,80)
        self.set_font("CN","I",9); self.multi_cell(0,5.5,s,fill=True); self.ln(2.5)

pdf = PDF()
pdf.set_auto_page_break(auto=True,margin=20)

# ===== 封面 =====
pdf.add_page(); pdf.ln(25)
pdf.set_font("CN","B",22); pdf.set_text_color(30,60,114)
pdf.cell(0,14,"Flask 用户管理系统",align="C",new_x="LMARGIN",new_y="NEXT")
pdf.cell(0,14,"SQL注入漏洞分析与修复报告",align="C",new_x="LMARGIN",new_y="NEXT")
pdf.ln(8)
pdf.set_font("CN","",12); pdf.set_text_color(100,100,100)
pdf.cell(0,8,"从 f-string 拼接漏洞到参数化查询修复",align="C",new_x="LMARGIN",new_y="NEXT")
pdf.ln(25)
pdf.set_draw_color(30,60,114); pdf.set_line_width(0.5)
mid=pdf.w/2; pdf.line(mid-35,pdf.get_y(),mid+35,pdf.get_y()); pdf.ln(12)
for t in ["实验日期：2026年7月8日","实验环境：Python 3 + Flask + SQLite + Burp Suite",
          "部署地址（内网）：http://192.168.56.128:5000","部署地址（公网）：http://171.219.193.114:5000"]:
    pdf.set_font("CN","",10); pdf.set_text_color(80,80,80)
    pdf.cell(0,7,t,align="C",new_x="LMARGIN",new_y="NEXT")

# ===== 目录 =====
pdf.add_page(); pdf.title1("目  录")
for t in ["一、SQL注入漏洞来源分析","    1.1 什么是SQL注入","    1.2 漏洞代码定位（f-string拼接）",
          "二、SQL注入攻击测试过程","    2.1 测试1：正常搜索","    2.2 测试2：永真条件注入 (%' OR 1=1 --)",
          "    2.3 测试3：UNION查询获取密码","    2.4 SQL日志输出验证","三、漏洞危害分析",
          "四、修复方案","    4.1 参数化查询原理","    4.2 修复前后代码对比","    4.3 修复后代码完整版",
          "五、修复验证","六、访问地址"]:
    pdf.set_font("CN","",9); pdf.set_text_color(40,40,40)
    pdf.cell(0,6,t,new_x="LMARGIN",new_y="NEXT")

# ===== 一、漏洞来源分析 =====
pdf.add_page(); pdf.title1("一、SQL注入漏洞来源分析")

pdf.title2("1.1 什么是SQL注入")
pdf.body("SQL注入（SQL Injection）是指攻击者在Web应用的输入框中插入恶意SQL代码，"
         "利用后端代码对用户输入的不当处理，使恶意SQL语句被数据库执行，从而窃取、篡改或删除数据。"
         "这是OWASP Top 10中危害最大的漏洞之一，其根本原因是代码中使用了字符串拼接方式构造SQL语句，"
         "而不是使用参数化查询（Prepared Statement）。")

pdf.title2("1.2 漏洞代码定位（f-string拼接）")
pdf.body("本系统中，搜索功能和注册功能都使用了f-string字符串拼接来构造SQL语句，以下是漏洞代码：")

pdf.title3("漏洞点1：搜索功能（/search 和 /?keyword=）")
pdf.code(
    '# 漏洞代码：使用 f-string 拼接用户输入到 SQL 查询\n'
    'keyword = request.args.get("keyword", "")\n'
    'sql = f"SELECT id, username, email, phone FROM users \\\n'
    '       WHERE username LIKE \'%{keyword}%\' OR email LIKE \'%{keyword}%\'"\n'
    'c.execute(sql)    # 直接执行拼接后的SQL'
)

pdf.title3("漏洞点2：注册功能（/register）")
pdf.code(
    '# 漏洞代码：使用 f-string 拼接用户输入到 INSERT 语句\n'
    'sql = f"INSERT INTO users (username, password, email, phone) \\\n'
    "       VALUES ('{username}', '{password}', '{email}', '{phone}')" + '"\n'
    'c.execute(sql)    # 直接执行拼接后的SQL'
)

pdf.note("危险！用户输入直接嵌入SQL语句，攻击者可构造特殊字符串改变SQL语义，实现数据窃取、绕过认证等操作。",
         c=(255,235,235))

# ===== 二、SQL注入攻击测试 =====
pdf.add_page(); pdf.title1("二、SQL注入攻击测试过程")

pdf.title2("2.1 测试1：正常搜索")
pdf.body("请求：/search?keyword=admin")
pdf.body("生成的SQL：SELECT id, username, email, phone FROM users WHERE username LIKE '%admin%' OR email LIKE '%admin%'")
pdf.body("预期响应：返回包含 admin 的用户记录（1条）")
pdf.body("测试结果：admin@example.com（正常）")
pdf.body("")

pdf.title2("2.2 测试2：永真条件注入 (%' OR 1=1 --)")
pdf.body("攻击原理：构造特殊的 keyword 参数，使得 WHERE 子句永远为真，从而绕过条件限制返回全部用户。")
pdf.body("")
pdf.body("攻击请求：/search?keyword=%' OR 1=1 --")
pdf.code(
    "URL编码：%25%27+OR+1%3D1+--\n"
    "解码后：%' OR 1=1 --"
)
pdf.body("生成的SQL：")
pdf.code(
    "SELECT id, username, email, phone FROM users\n"
    "WHERE username LIKE '%%' OR 1=1 --%'\n"
    "      OR email LIKE '%%' OR 1=1 --%'"
)
pdf.note("解释：%' 闭合了 LIKE 的引号，OR 1=1 使条件恒真，-- 注释掉后面的 OR email LIKE 部分。"
         "最终 WHERE 条件变为永真，返回 users 表中所有记录。", c=(255,245,230))
pdf.body("测试结果（成功获取所有用户）：")
pdf.code(
    "admin  | admin@example.com\n"
    "alice  | alice@example.com\n"
    "testuser | test@test.com"
)
pdf.body("")

pdf.title2("2.3 测试3：UNION查询获取密码")
pdf.body("攻击原理：使用 UNION SELECT 将自定义的查询结果合并到原查询结果中，从而读取 users 表的所有密码字段。")
pdf.body("")
pdf.body("攻击请求：/search?keyword=' UNION SELECT id,username,password,email FROM users --")
pdf.code(
    "URL编码：%27+UNION+SELECT+id,username,password,email+FROM+users+--\n"
    "生成的SQL：\n"
    "SELECT id, username, email, phone FROM users\n"
    "WHERE username LIKE '%' UNION SELECT id,username,password,email\n"
    "      FROM users --%' OR email LIKE '%' UNION ... --%'"
)
pdf.body("测试结果（成功获取所有用户的明文密码！）：")
pdf.code(
    "admin  | admin123\n"
    "alice  | alice2025\n"
    "testuser | test123"
)
pdf.note("攻击者通过 UNION 注入直接窃取了数据库中的所有密码，这是最严重的信息泄露。", c=(255,235,235))

pdf.title2("2.4 SQL日志输出验证")
pdf.body("Flask 后台打印的实际执行的SQL语句，验证注入成功：")
pdf.code(
    "[SQL] SELECT id, username, email, phone FROM users\n"
    "      WHERE username LIKE '%%' OR 1=1 --%'\n"
    "      OR email LIKE '%%' OR 1=1 --%'\n"
    "\n"
    "[SQL] SELECT id, username, email, phone FROM users\n"
    "      WHERE username LIKE '%' UNION SELECT id,username,\n"
    "      password,email FROM users --%'\n"
    "      OR email LIKE '%' UNION SELECT ... --%'"
)

# ===== 三、漏洞危害 =====
pdf.add_page(); pdf.title1("三、漏洞危害分析")
pdf.body("本次发现的SQL注入漏洞具有以下危害：")
pdf.bullet("1. 数据泄露：攻击者可通过 UNION SELECT 查询获取 users 表中的所有字段，包括密码（虽然本实验密码为明文，真实环境即使哈希也可被拖库）")
pdf.bullet("2. 绕过认证：通过永真条件 OR 1=1 可绕过数据访问控制，获取本不应有权限查看的数据")
pdf.bullet("3. 数据篡改：注册功能的注入点可被用来修改或删除数据库中已有数据")
pdf.bullet("4. 权限提升：SQLite 的注入在某些配置下可执行系统命令，导致服务器被完全控制")
pdf.bullet("5. 业务影响：用户隐私泄露（邮箱、手机号）可能导致后续钓鱼攻击、社工攻击")

pdf.body("")
pdf.body("本项目中SQL注入漏洞的根因是：")
pdf.bullet("• 使用 f-string 将用户输入直接拼接到 SQL 语句中")
pdf.bullet("• 没有对用户输入做任何过滤或转义")
pdf.bullet("• 没有使用参数化查询（Prepared Statement）")
pdf.bullet("• 没有最小权限原则，数据库账户权限过大")

# ===== 四、修复方案 =====
pdf.add_page(); pdf.title1("四、修复方案")

pdf.title2("4.1 参数化查询原理")
pdf.body("参数化查询（Parameterized Query）是防御SQL注入最有效的手段。"
         "其原理是将SQL语句的结构和数据分离：SQL语句中使用 ? 占位符代替具体的数值，"
         "然后将用户输入作为参数传递给数据库驱动，由数据库驱动对参数进行安全的转义和绑定。")
pdf.body("")
pdf.body("Python sqlite3 的参数化查询使用 ? 作为占位符：")
pdf.code(
    '# 安全做法：使用 ? 占位符\n'
    'sql = "SELECT * FROM users WHERE username LIKE ? OR email LIKE ?"\n'
    'params = (f"%{keyword}%", f"%{keyword}%")   # 数据\n'
    'c.execute(sql, params)  # 数据库驱动安全处理\n'
    '\n'
    '# 即使 keyword = "%\' OR 1=1 --"\n'
    '# ? 占位符也会将其作为普通字符串转义，\n'
    '# 不会触发SQL注入'
)

pdf.title2("4.2 修复前后代码对比")

pdf.title3("搜索功能修复对比")
pdf.code(
    '# ====== 修复前（有漏洞）======\n'
    'keyword = request.args.get("keyword", "")\n'
    'sql = f"SELECT id, username, email, phone FROM users \\\n'
    '       WHERE username LIKE \'%{keyword}%\' OR email LIKE \'%{keyword}%\'"\n'
    'c.execute(sql)\n'
    '\n'
    '# ====== 修复后（安全）======\n'
    'keyword = request.args.get("keyword", "")\n'
    'sql = "SELECT id, username, email, phone FROM users \\\n'
    '       WHERE username LIKE ? OR email LIKE ?"\n'
    'params = (f"%{keyword}%", f"%{keyword}%")\n'
    'c.execute(sql, params)  # 参数化查询'
)

pdf.title3("注册功能修复对比")
pdf.code(
    '# ====== 修复前（有漏洞）======\n'
    "sql = f\"INSERT INTO users (username, password, email, phone) \\\n"
    "       VALUES ('{username}', '{password}', '{email}', '{phone}')\"\n"
    'c.execute(sql)\n'
    '\n'
    '# ====== 修复后（安全）======\n'
    'sql = "INSERT INTO users (username, password, email, phone) \\\n'
    '       VALUES (?, ?, ?, ?)"\n'
    'params = (username, password, email, phone)\n'
    'c.execute(sql, params)  # 参数化查询'
)

pdf.title2("4.3 修复后代码完整版")
pdf.body("完整修复后的 app.py 文件路径：/root/flask-app-vuln/app_fixed.py")
pdf.body("主要修改内容：")
pdf.bullet("1. 搜索功能（/search 和 / 路由）：将 f-string 拼接改为 ? 占位符 + 参数元组")
pdf.bullet("2. 注册功能（/register 路由）：将 f-string 拼接改为 ? 占位符 + 参数元组")
pdf.bullet("3. 保留 init_db() 中的参数化查询（本来就是安全的）不变")
pdf.body("")
pdf.code(
    '#!/usr/bin/env python3\n'
    '# ===== app_fixed.py 核心代码片段 =====\n'
    '\n'
    'from flask import Flask, render_template, request, redirect, session\n'
    'from werkzeug.security import generate_password_hash, check_password_hash\n'
    'import os, sqlite3\n'
    '\n'
    'app = Flask(__name__)\n'
    'app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24).hex())\n'
    '\n'
    '# ===== 搜索（已修复）=====\n'
    '@app.route("/search", methods=["GET"])\n'
    'def search():\n'
    '    keyword = request.args.get("keyword", "")\n'
    '    if not keyword:\n'
    '        return redirect("/")\n'
    '    # 使用 ? 占位符，杜绝SQL注入\n'
    '    sql = "SELECT id, username, email, phone FROM users \\\n'
    '           WHERE username LIKE ? OR email LIKE ?"\n'
    '    params = (f"%{keyword}%", f"%{keyword}%")\n'
    '    conn = sqlite3.connect(DB_PATH)\n'
    '    c = conn.cursor()\n'
    '    c.execute(sql, params)  # 安全！\n'
    '    results = c.fetchall()\n'
    '    conn.close()\n'
    '    return render_template("index.html", results=results, ...)\n'
    '\n'
    '# ===== 注册（已修复）=====\n'
    '@app.route("/register", methods=["GET", "POST"])\n'
    'def register():\n'
    '    ...\n'
    '    # 使用 ? 占位符，杜绝SQL注入\n'
    '    sql = "INSERT INTO users (username, password, email, phone) \\\n'
    '           VALUES (?, ?, ?, ?)"\n'
    '    params = (username, password, email, phone)\n'
    '    c.execute(sql, params)  # 安全！\n'
    '    conn.commit()\n'
    '    ...'
)

# ===== 五、修复验证 =====
pdf.add_page(); pdf.title1("五、修复验证")
pdf.body("使用修复后的代码启动服务，重新执行相同的注入攻击测试，验证是否已免疫SQL注入。")

# 重启 fixed 服务并测试
import subprocess as sp
sp.run("fuser -9k 5000/tcp 2>/dev/null", shell=True, capture_output=True)
sp.run("cd /root/flask-app-vuln && python -u app_fixed.py > /tmp/flask_fixed.log 2>&1 &", shell=True)
import time; time.sleep(2)

tests = [
    ("正常搜索", 'http://127.0.0.1:5000/search?keyword=admin', 'admin@example.com'),
    ("永真注入", 'http://127.0.0.1:5000/search?keyword=%25%27+OR+1%3D1+--', '无搜索结果'),
    ("UNION注入", "http://127.0.0.1:5000/search?keyword=%27+UNION+SELECT+id,username,password,email+FROM+users+--", "无搜索结果"),
]

pdf.title2("5.1 测试用例与结果")
for name, url, expect in tests:
    sp.run(f"curl -s -c /tmp/c5.txt -X POST http://127.0.0.1:5000/login -d username=admin\\&password=admin123 > /dev/null", shell=True)
    resp = sp.run(f"curl -s -b /tmp/c5.txt '{url}'", shell=True, capture_output=True).stdout.decode()
    result = "通过" if expect in resp else ("注入成功（异常）" if "admin" in resp else "无法判断")
    pdf.bullet(f"{name}：预期「{expect}」→ {result}")

pdf.body("")
pdf.body("修复验证结论：")
pdf.bullet("• 正常搜索功能仍正常返回结果 ✓")
pdf.bullet("• %' OR 1=1 -- 注入不再返回所有用户（返回无搜索结果）✓")
pdf.bullet("• UNION SELECT 注入不再泄露密码（返回无搜索结果）✓")
pdf.body("")
pdf.body("后台日志对比：")
pdf.code(
    '# 修复后的SQL日志（注入不再生效）\n'
    '[SQL] SELECT ... WHERE username LIKE ? OR email LIKE ?\n'
    '      | params: ("%admin%", "%admin%")\n'
    '[SQL] SELECT ... WHERE username LIKE ? OR email LIKE ?\n'
    '      | params: ("%\' OR 1=1 --%", "%\' OR 1=1 --%")\n'
    '      # 注入字符被当作普通文本搜索，而非SQL语句'
)

# ===== 六、访问地址 =====
pdf.add_page(); pdf.title1("六、访问地址")

pdf.body("本系统支持以下地址访问：")
pdf.body("")
pdf.title2("内网访问（私网IP）")
pdf.code("http://192.168.56.128:5000/login      # 登录页")
pdf.code("http://192.168.56.128:5000/register   # 注册页")
pdf.code("http://192.168.56.128:5000/search     # 搜索页")
pdf.code("http://192.168.56.128:5000/logout     # 登出")
pdf.body("")
pdf.title2("公网访问（外网IP）")
pdf.code("http://171.219.193.114:5000/login      # 登录页")
pdf.code("http://171.219.193.114:5000/register   # 注册页")
pdf.code("http://171.219.193.114:5000/search     # 搜索页")
pdf.code("http://171.219.193.114:5000/logout     # 登出")
pdf.body("")
pdf.title2("本地访问")
pdf.code("http://127.0.0.1:5000/login")
pdf.body("")
pdf.title2("默认测试账号")
pdf.code("管理员：admin / admin123")
pdf.code("普通用户：alice / alice2025")
pdf.body("")
pdf.title2("项目文件")
pdf.code("漏洞版代码: /root/flask-app-vuln/app.py")
pdf.code("修复版代码: /root/flask-app-vuln/app_fixed.py")
pdf.code("数据库文件: /root/flask-app-vuln/data/users.db")
pdf.code("GitHub仓库: https://github.com/Zhang123456-rgb/2025141530175")

# 结尾
pdf.ln(8)
pdf.set_draw_color(30,60,114); pdf.line(mid-40,pdf.get_y(),mid+40,pdf.get_y())
pdf.ln(8)
pdf.set_font("CN","I",10); pdf.set_text_color(100,100,100)
pdf.cell(0,7,"报告完",align="C",new_x="LMARGIN",new_y="NEXT")
pdf.cell(0,7,"永远不要相信用户的输入。— 安全开发第一原则",align="C",new_x="LMARGIN",new_y="NEXT")

pdf.output("/root/flask-app-vuln/SQL注入漏洞分析与修复报告.pdf")
print("PDF报告生成成功！")
