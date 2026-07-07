#!/usr/bin/env python3
"""
Flask 用户管理系统 - 安全漏洞分析与修复实验报告
版本：v2.0（根据评审意见全面修订）
"""

from fpdf import FPDF

class ReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("CN", "", "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
        self.add_font("CN", "B", "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
        self.add_font("CN", "I", "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
        self.add_font("CNMono", "", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")

    def header(self):
        if self.page_no() > 1:
            self.set_font("CN", "I", 8)
            self.cell(0, 8, "Flask 用户管理系统 - 安全漏洞分析与修复实验报告", align="C")
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("CN", "I", 8)
        self.cell(0, 10, f"第 {self.page_no()} 页", align="C")

    def cover_title(self, text, size=26):
        self.set_font("CN", "B", size)
        self.set_text_color(30, 60, 114)
        self.cell(0, 15, text, align="C", new_x="LMARGIN", new_y="NEXT")

    def cover_sub(self, text, size=13):
        self.set_font("CN", "", size)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, text, align="C", new_x="LMARGIN", new_y="NEXT")

    def title_section(self, title):
        self.set_font("CN", "B", 15)
        self.set_text_color(30, 60, 114)
        self.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 60, 114)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)

    def sub_title(self, title):
        self.set_font("CN", "B", 12)
        self.set_text_color(50, 90, 150)
        self.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def sub_sub_title(self, title):
        self.set_font("CN", "B", 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text):
        self.set_font("CN", "", 9)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(1.5)

    def bullet(self, text, indent=4):
        self.set_font("CN", "", 9)
        self.set_text_color(40, 40, 40)
        self.set_x(self.l_margin + indent)
        self.multi_cell(self.w - self.l_margin - self.r_margin - indent, 5.5, text)
        self.ln(0.5)

    def code(self, code):
        self.set_fill_color(240, 242, 245)
        self.set_text_color(30, 30, 30)
        self.set_font("CNMono", "", 7.5)
        for line in code.split("\n"):
            w = self.w - self.l_margin - self.r_margin
            self.cell(w, 4.8, "  " + line, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2.5)

    def note_box(self, text, color=(240, 248, 255)):
        self.set_fill_color(*color)
        self.set_text_color(40, 60, 80)
        self.set_font("CN", "I", 9)
        self.multi_cell(0, 5.5, text, fill=True)
        self.ln(2.5)

    def diff_table(self, rows, col_headers=None):
        """Render a small table. rows is list of lists."""
        if col_headers is None:
            col_headers = ["项目", "修改前", "修改后"]
        n = len(col_headers)
        col_w = (self.w - self.l_margin - self.r_margin) / n

        self.set_font("CN", "B", 8)
        self.set_fill_color(30, 60, 114)
        self.set_text_color(255, 255, 255)
        for h in col_headers:
            self.cell(col_w, 7, h, border=1, align="C", fill=True)
        self.ln()

        self.set_font("CN", "", 7.5)
        for row in rows:
            self.set_text_color(40, 40, 40)
            # Calculate max height needed
            max_lines = 1
            for cell_text in row:
                lines = len(cell_text) // 30 + 1  # rough estimate
                if lines > max_lines:
                    max_lines = lines
            h = max(7, max_lines * 5)
            for i, cell_text in enumerate(row):
                # Alternate row colors
                if rows.index(row) % 2 == 0:
                    self.set_fill_color(248, 249, 250)
                else:
                    self.set_fill_color(255, 255, 255)
                self.cell(col_w, h, cell_text, border=1, align="C", fill=True)
            self.ln()
        self.ln(3)


def build_pdf():
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ===================================================================
    # 封面
    # ===================================================================
    pdf.add_page()
    pdf.ln(30)
    pdf.cover_title("Flask 用户管理系统")
    pdf.cover_title("安全漏洞分析与修复实验报告", 20)
    pdf.ln(8)
    pdf.cover_sub("Web 安全实验教学项目", 14)
    pdf.ln(6)
    pdf.set_font("CN", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 7, "Python Flask  |  Werkzeug  |  Burp Suite  |  Session 安全", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_draw_color(30, 60, 114)
    pdf.set_line_width(0.5)
    mid = pdf.w / 2
    pdf.line(mid - 35, pdf.get_y(), mid + 35, pdf.get_y())
    pdf.ln(12)
    info_lines = [
        "实验环境：Python 3.10+ | Flask 2.3.x | werkzeug.security | Burp Suite Community v2024",
        "实验日期：2026 年 7 月 7 日",
        "实验目的：识别并修复 Web 登录模块的四类安全漏洞（密码明文、会话伪造、信息泄露、暴力破解）",
        "部署地址：http://127.0.0.1:5000",
    ]
    for line in info_lines:
        pdf.set_font("CN", "", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 7, line, align="C", new_x="LMARGIN", new_y="NEXT")

    # ===================================================================
    # 目录
    # ===================================================================
    pdf.add_page()
    pdf.title_section("目  录")
    toc_items = [
        "一、实验概述",
        "    1.1  实验环境",
        "    1.2  实验目的",
        "    1.3  项目架构",
        "二、漏洞一（高危）：用户密码明文存储与前端回显",
        "    2.1  漏洞原理",
        "    2.2  漏洞复现操作（Burp Suite 实验流程）",
        "    2.3  实际危害",
        "    2.4  修复方案与代码对比",
        "    2.5  长期加固建议",
        "三、漏洞二（高危）：Flask 会话密钥硬编码",
        "    3.1  漏洞原理",
        "    3.2  漏洞复现操作（Session 伪造实验流程）",
        "    3.3  实际危害",
        "    3.4  修复方案与代码对比",
        "    3.5  长期加固建议",
        "四、漏洞三（中危）：HTML 注释泄露管理员凭证",
        "    4.1  漏洞原理",
        "    4.2  漏洞复现操作",
        "    4.3  实际危害",
        "    4.4  修复方案与代码对比",
        "    4.5  长期加固建议",
        "五、漏洞四（中危）：登录接口无防暴力破解机制",
        "    5.1  漏洞原理",
        "    5.2  漏洞复现操作（Burp Intruder 字典爆破流程）",
        "    5.3  实际危害",
        "    5.4  修复方案（代码实现）",
        "    5.5  长期加固建议",
        "六、修改对照总表",
        "七、修复验证测试",
        "    7.1  测试用例与结果",
        "    7.2  Burp 抓包验证说明",
        "八、实验总结与安全开发规范",
        "    8.1  实验总结",
        "    8.2  安全开发规范 Checklist",
        "    8.3  延伸加固方案",
    ]
    for item in toc_items:
        pdf.set_font("CN", "", 9)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 6, item, new_x="LMARGIN", new_y="NEXT")

    # ===================================================================
    # 一、实验概述
    # ===================================================================
    pdf.add_page()
    pdf.title_section("一、实验概述")

    pdf.sub_title("1.1  实验环境")
    pdf.bullet("• 开发语言：Python 3.10+")
    pdf.bullet("• Web 框架：Flask 2.3.x（Werkzeug 2.3.x + Jinja2 3.x）")
    pdf.bullet("• 密码工具：werkzeug.security（generate_password_hash / check_password_hash，PBKDF2+sha256）")
    pdf.bullet("• 安全测试工具：Burp Suite Community Edition v2024.x")
    pdf.bullet("• 字典爆破工具：Burp Intruder + rockyou.txt（/usr/share/wordlists/rockyou.txt）")
    pdf.bullet("• Session 分析工具：flask-unsign / itsdangerous 库")
    pdf.bullet("• 网络抓包工具：Burp Proxy（监听 127.0.0.1:8080）")
    pdf.bullet("• 部署地址：http://127.0.0.1:5000")
    pdf.bullet("• 实验日期：2026 年 7 月 7 日")

    pdf.sub_title("1.2  实验目的")
    pdf.bullet("• 理解 Web 应用中密码明文存储与传输的安全风险")
    pdf.bullet("• 掌握 Flask Session 签名机制及密钥泄露导致的会话伪造攻击")
    pdf.bullet("• 认识前端注释泄露敏感信息的危害")
    pdf.bullet("• 掌握 Burp Suite 抓包、Intruder 字典爆破等渗透测试基本操作")
    pdf.bullet("• 学习使用 werkzeug.security 进行密码哈希存储与安全比对")
    pdf.bullet("• 学习登录接口防暴力破解的基本策略")

    pdf.sub_title("1.3  项目架构")
    pdf.code(
        "flask-app-vuln/\n"
        "  app.py                  # main app (routes, user DB, login logic)\n"
        "  templates/\n"
        "    base.html             # base template (navbar, layout)\n"
        "    index.html            # home page (user info display)\n"
        "    login.html            # login page\n"
        "  static/css/\n"
        "    style.css             # global styles"
    )
    pdf.body("")

    # ===================================================================
    # 二、漏洞一（高危）：用户密码明文存储与前端回显
    # ===================================================================
    pdf.add_page()
    pdf.title_section("二、漏洞一（高危）：用户密码明文存储与前端回显")

    pdf.sub_title("2.1  漏洞原理")
    pdf.body(
        "在 app.py 的 USERS 字典中，密码以纯文本形式直接存储（例如 \"password\": \"admin123\"）。"
        "登录验证时，使用 == 运算符直接将用户输入的密码与字典中的明文密码进行字符串比较。"
        "登录成功后，将包含 password 字段的完整用户字典传递给模板，"
        "模板中的 {{ user.password }} 将密码原文输出到 HTML 页面。"
    )
    pdf.body(
        "该漏洞违反 OWASP Top 10 中 \"A02:2021 – Cryptographic Failures\"（加密机制失效）安全要求。"
        "正确的做法是使用不可逆的哈希算法（如 bcrypt、PBKDF2、Argon2）对密码进行摘要存储，"
        "且永远不应将密码字段传递给前端模板渲染。"
    )

    pdf.sub_title("2.2  漏洞复现操作（Burp Suite 实验流程）")
    pdf.body("步骤一：启动 Flask 应用，访问 http://localhost:5000/login")
    pdf.body("步骤二：在浏览器中使用默认管理员账号 admin / admin123 登录")
    pdf.body("步骤三：登录成功后跳转到首页，页面直接显示明文密码 \"admin123\"")
    pdf.body("步骤四：按 F12 打开开发者工具 → Elements 面板，定位到用户信息列表，可直接看到密码原文")
    pdf.body("步骤五：启动 Burp Suite，配置浏览器代理（127.0.0.1:8080）")
    pdf.body("步骤六：使用 Burp Proxy 拦截登录 POST 请求：")
    pdf.body("      POST /login HTTP/1.1")
    pdf.body("      username=admin&password=admin123")
    pdf.body("步骤七：观察请求体，密码以明文形式在 HTTP 中传输，无任何加密保护")
    pdf.body("步骤八：将拦截到的数据包发送至 Repeater，可重复发送验证登录行为")

    pdf.sub_title("2.3  实际危害")
    pdf.bullet("• 数据库泄露（如字典被 dump）后，所有用户密码直接暴露")
    pdf.bullet("• 攻击者可利用泄露的密码在其他平台尝试撞库攻击（Credential Stuffing）")
    pdf.bullet("• 前端页面暴露密码，任何能查看页面源代码的人都能获取")
    pdf.bullet("• HTTP 明文传输，中间人攻击（MITM）可截获登录凭证")

    pdf.sub_title("2.4  修复方案与代码对比")
    pdf.body("修复一：app.py - 新增安全库导入与密码哈希化")
    pdf.diff_table([
        ["密码存储", '"password": "admin123"', 'generate_password_hash("admin123")'],
        ["密码比对", '== password', 'check_password_hash(...)'],
        ["导入语句", "无安全导入", "from werkzeug.security import ..."],
    ], ["修改项", "修改前", "修改后"])

    pdf.body("修复二：index.html - 禁止模板输出密码字段（注意：最优方案是后端完全不传递 password 字段，而非仅前端掩码）")
    pdf.diff_table([
        ["密码显示", "{{ user.password }}\n直接输出密码原文", "********（已加密保护）\n或彻底移除password字段渲染"],
    ], ["修改项", "修改前", "修改后"])

    pdf.code(
        "<!-- BEFORE (vulnerable line) -->\n"
        '<li><strong>密码：</strong>{{ user.password }}</li>\n'
        "\n"
        "<!-- AFTER (fixed) -->\n"
        '<li><strong>密码：</strong>********（已加密保护）</li>\n'
        "<!-- BEST: dont render password field at all -->\n"
        "<!-- exclude password from dict passed to template -->"
    )

    pdf.sub_title("2.5  长期加固建议")

    pdf.sub_title("2.5  长期加固建议")
    pdf.bullet("• 使用 bcrypt 或 Argon2 替代 PBKDF2 作为密码哈希算法")
    pdf.bullet("• 后端模板渲染时彻底不传递 password 字段，而非仅前端掩码")
    pdf.bullet("• 线上部署强制启用 HTTPS，避免 HTTP 传输密码明文被抓包")
    pdf.bullet("• 禁止在任何日志中打印用户密码")
    pdf.bullet("• 定期使用密码泄露检测工具（如 Have I Been Pwned API）检查密码是否已泄露")

    # ===================================================================
    # 三、漏洞二（高危）：Flask 会话密钥硬编码
    # ===================================================================
    pdf.add_page()
    pdf.title_section("三、漏洞二（高危）：Flask 会话密钥硬编码")

    pdf.sub_title("3.1  漏洞原理")
    pdf.body(
        "Flask 使用基于 itsdangerous 库的签名机制来保护 session cookie。服务器使用 secret_key "
        "对 session 数据进行 HMAC 签名，以确保数据在传输过程中未被篡改。"
    )
    pdf.body(
        "当 secret_key 设置为固定的弱密钥（如 \"dev-key-2025\"）时，攻击者可以从源代码中获取该密钥，"
        "利用 flask-unsign 或 itsdangerous 库对劫持到的 session cookie 进行解签、篡改载荷后重新签名，"
        "从而伪造任意用户的会话身份。"
    )
    pdf.body(
        "注意：此漏洞属于 \"会话管理不安全\"（Insecure Session Management），"
        "严格来说不是 \"弱密码\" 问题。正确术语为：Flask Session 签名密钥硬编码导致的会话伪造攻击"
        "（Session Forgery / Session Manipulation）。"
    )

    pdf.sub_title("3.2  漏洞复现操作（Session 伪造实验流程）")
    pdf.body("步骤一：正常登录系统（admin/admin123），使用 Burp 或浏览器开发者工具获取 Cookie")
    pdf.body("步骤二：提取 session 值（Flask 默认的 session cookie 名为 session）")
    pdf.body("步骤三：在终端中使用 flask-unsign 工具解签 session 数据：")
    pdf.code(
        "# decode session cookie\n"
        "flask-unsign --decode --cookie '<session_value>'\n"
        "\n"
        "# if secret key is known, verify by unsigning\n"
        "flask-unsign --unsign --cookie '<session_value>' --secret 'dev-key-2025'"
    )
    pdf.body("步骤四：篡改 session 载荷，将 username 改为 admin：")
    pdf.code(
        "# forge session for any user\n"
        "flask-unsign --sign --cookie \"{'username':'admin'}\" --secret 'dev-key-2025'"
    )
    pdf.body("步骤五：将伪造的 session cookie 注入浏览器，刷新页面后可无需密码以 admin 身份登录")
    pdf.body("步骤六：使用 Burp Repeater 修改请求中的 Cookie 头，验证无需密码即可登录")

    pdf.sub_title("3.3  实际危害")
    pdf.bullet("• 攻击者可伪造任意用户的 session，实现无需密码的身份冒充")
    pdf.bullet("• 可伪造管理员会话，获取系统最高权限")
    pdf.bullet("• 会话劫持配合信息泄露可导致完全的系统沦陷")
    pdf.bullet("• 由于密钥硬编码在代码中，所有部署实例使用相同密钥，漏洞影响面广")

    pdf.sub_title("3.4  修复方案与代码对比")

    pdf.body("修复说明一：禁止使用 os.urandom(24).hex() 作为修复方案，因为每次重启服务后所有已有 session 会失效，"
             "强制全部用户下线是生产环境不可接受的可用性问题。")

    pdf.body("修复说明二：正确的方案是从环境变量中读取 secret_key。开发环境可在 .env 文件中配置固定密钥"
             "（但需打印醒目警告提醒不应用于生产），生产环境必须从环境变量或密钥管理服务"
             "（如 AWS Secrets Manager / HashiCorp Vault）中读取。")

    pdf.code(
        "# CORRECT approach (production)\n"
        "import os\n"
        "import secrets\n"
        "\n"
        "app.secret_key = os.environ.get('SECRET_KEY')\n"
        "if not app.secret_key:\n"
        "    if os.environ.get('FLASK_ENV') == 'development':\n"
        "        # dev only: allow default with prominent warning\n"
        '        print(\"WARNING: Using default SECRET_KEY in development!\")\n'
        "        app.secret_key = 'dev-secret-key-do-not-use-in-production'\n"
        "    else:\n"
        '        raise ValueError(\"SECRET_KEY environment variable is required\")'
    )

    pdf.sub_title("3.5  长期加固建议")
    pdf.bullet("• 生产环境 secret_key 通过环境变量注入，长度至少 64 位随机字符")
    pdf.bullet("• 限制 session 有效期，设置 permanent_session_lifetime")
    pdf.bullet("• 增加 session IP 绑定校验（session['ip'] = request.remote_addr）")
    pdf.bullet("• 敏感操作（修改密码、转账等）要求二次身份验证")
    pdf.bullet("• 定期轮换 secret_key，配合 session 过期策略")

    # ===================================================================
    # 四、漏洞三（中危）：HTML 注释泄露管理员凭证
    # ===================================================================
    pdf.add_page()
    pdf.title_section("四、漏洞三（中危）：HTML 注释泄露管理员凭证")

    pdf.sub_title("4.1  漏洞原理")
    pdf.body(
        "login.html 文件第 1 行包含一条 HTML 注释："
    )
    pdf.code("<!-- DEBUG - default admin account: admin / admin123 -->")
    pdf.body(
        "HTML 注释虽然在浏览器页面上不可见，但任何用户通过 \"查看页面源代码\"（Ctrl+U / F12 开发者工具）"
        "即可直接读取注释内容，获取管理员的登录凭证。"
    )
    pdf.body(
        "这是典型的 \"前端敏感信息泄露\"（Sensitive Data Exposure in Frontend），"
        "属于 OWASP Top 10 中 A05:2021 – Security Misconfiguration 的范畴。"
    )

    pdf.sub_title("4.2  漏洞复现操作")
    pdf.body("步骤一：访问 http://localhost:5000/login")
    pdf.body("步骤二：在页面上右键 → 选择 \"查看页面源代码\"（或按 Ctrl+U）")
    pdf.body("步骤三：在 HTML 顶部看到注释中的账号密码：admin / admin123")
    pdf.body("步骤四：使用 Burp Proxy 拦截登录页面响应，Response Body 中同样包含该注释")
    pdf.body("步骤五：直接使用泄露的凭证登录系统，验证信息真实性")

    pdf.sub_title("4.3  实际危害")
    pdf.bullet("• 低权限用户可获取管理员账号密码，实现越权访问")
    pdf.bullet("• 源码管理（Git）中若包含该文件，历史版本将永久记录该凭证")
    pdf.bullet("• 搜索引擎可能索引页面内容，导致凭证泄露范围扩大")

    pdf.sub_title("4.4  修复方案与代码对比")
    pdf.diff_table([
        ["注释内容", "admin / admin123", "请联系管理员获取账号"],
    ], ["修改项", "修改前", "修改后"])

    pdf.code(
        "<!-- BEFORE (vulnerable) -->\n"
        "<!-- DEBUG - default admin account: admin / admin123 -->\n"
        "\n"
        "<!-- AFTER (fixed) -->\n"
        "<!-- DEBUG - contact admin for credentials -->"
    )

    pdf.sub_title("4.5  长期加固建议")
    pdf.bullet("• 建立上线前检查清单（Checklist），全面清理所有调试注释")
    pdf.bullet("• 禁止在前端 HTML、JavaScript、CSS 中写入任何密钥、接口凭证")
    pdf.bullet("• 使用环境变量控制调试模式，生产环境禁用 debug 信息输出")
    pdf.bullet("• 在 CI/CD 流程中加入关键词扫描（如 \"password\"、\"secret\"、\"admin\"）")
    pdf.bullet("• 默认账号密码应在系统初始化时强制修改，不得写死在代码或页面中")

    # ===================================================================
    # 五、漏洞四（中危）：登录接口无防暴力破解机制
    # ===================================================================
    pdf.add_page()
    pdf.title_section("五、漏洞四（中危）：登录接口无防暴力破解机制")

    pdf.sub_title("5.1  漏洞原理")
    pdf.body(
        "当前登录接口 /login 没有任何频率限制、失败次数锁定或验证码机制。"
        "攻击者可以使用 Burp Intruder 加载常见密码字典，对已知用户名（如 admin）进行批量密码枚举，"
        "通过响应内容的差异（\"用户名或密码错误！\" vs 跳转到首页）判断密码是否匹配。"
    )
    pdf.body(
        "这是典型的 \"不安全的登录接口设计\"，属于 OWASP Top 10 中 "
        "A07:2021 – Identification and Authentication Failures 的范畴。"
    )

    pdf.sub_title("5.2  漏洞复现操作（Burp Intruder 字典爆破流程）")
    pdf.body("步骤一：启动 Burp Suite，配置浏览器代理后访问 http://localhost:5000/login")
    pdf.body("步骤二：在登录表单中输入 admin / 任意密码，点击登录，Burp 拦截到 POST 请求：")
    pdf.code(
        "POST /login HTTP/1.1\n"
        "Host: 127.0.0.1:5000\n"
        "...\n"
        "username=admin&password=test123"
    )
    pdf.body("步骤三：右键数据包 → Send to Intruder")
    pdf.body("步骤四：在 Intruder 的 Positions 选项卡中，清除所有默认 Payload 位置")
    pdf.body("步骤五：选中 password=test123 中的 test123，点击 Add § 标记为 Payload 位置")
    pdf.body("步骤六：切换到 Payloads 选项卡，点击 Load 加载下载的字典文件（如 rockyou.txt 或 10k-common-passwords.txt）")
    pdf.body("步骤七：启动 Attack，观察每个请求的响应长度和状态码")
    pdf.body("步骤八：当响应长度明显不同（登录成功跳转首页 vs 返回错误提示）时，对应的密码即为正确密码")
    pdf.body("步骤九：找到 admin 的正确密码 admin123，验证爆破成功")

    pdf.sub_title("5.3  实际危害")
    pdf.bullet("• 无锁定机制，攻击者可无限枚举密码")
    pdf.bullet("• 字典爆破工具（Burp Intruder、hydra、medusa 等）可在数分钟内完成对弱密码的破解")
    pdf.bullet("• 结合漏洞三的泄露信息，爆破范围可更精准")
    pdf.bullet("• 大量错误登录请求可能影响服务器性能")

    pdf.sub_title("5.4  修复方案（代码实现）")
    pdf.body("以下提供两种方案的代码实现。方案一为本地开发用的内存计数器（简单但重启后失效）；"
             "方案二为生产环境推荐的 Redis 持久化计数器（支持多进程/多服务器）。")

    pdf.body("方案一：内存计数器（适合本地开发/单进程部署）")
    pdf.code(
        "# Option 1: in-memory counter (dev only)\n"
        "from collections import defaultdict\n"
        "from datetime import datetime, timedelta\n"
        "\n"
        "login_attempts = defaultdict(lambda: {'count': 0, 'lock_time': None})\n"
        "MAX_ATTEMPTS = 5\n"
        "LOCK_DURATION = timedelta(minutes=5)\n"
        "\n"
        "@app.route(\"/login\", methods=[\"GET\", \"POST\"])\n"
        "def login():\n"
        "    error = None\n"
        "    if request.method == \"POST\":\n"
        "        username = request.form.get(\"username\", \"\")\n"
        "        password = request.form.get(\"password\", \"\")\n"
        "        client_ip = request.remote_addr\n"
        "\n"
        "        # check if locked\n"
        "        record = login_attempts[client_ip]\n"
        "        if record['lock_time'] and datetime.now() < record['lock_time']:\n"
        "            remaining = (record['lock_time'] - datetime.now()).seconds\n"
        '            error = f\"登录过于频繁，请 {remaining} 秒后重试\"\n'
        "            return render_template(\"login.html\", error=error)\n"
        "\n"
        "        if username in USERS and check_password_hash(USERS[username][\"password\"], password):\n"
        "            # login OK, clear failure record\n"
        "            login_attempts[client_ip] = {'count': 0, 'lock_time': None}\n"
        "            session[\"username\"] = username\n"
        "            return render_template(\"index.html\", user=USERS[username])\n"
        "        else:\n"
        "            record['count'] += 1\n"
        "            if record['count'] >= MAX_ATTEMPTS:\n"
        "                record['lock_time'] = datetime.now() + LOCK_DURATION\n"
        '            error = \"用户名或密码错误！\"\n'
        "    return render_template(\"login.html\", error=error)"
    )

    pdf.body("方案二：Redis 持久化计数器（推荐生产环境使用，服务重启不丢失、支持多进程/多服务器）")
    pdf.code(
        "# Option 2: Redis persistent storage (production)\n"
        "import redis\n"
        "from datetime import timedelta\n"
        "\n"
        "r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)\n"
        "\n"
        "def check_login_lock(username):\n"
        '    \"\"\"检查账号是否被锁定，返回 (是否锁定, 提示信息)\"\"\"\n'
        '    key = f\"login_failures:{username}\"\n'
        "    failures = r.get(key)\n"
        "    if failures and int(failures) >= 5:\n"
        "        ttl = r.ttl(key)\n"
        "        if ttl > 0:\n"
        '            return True, f\"账号已锁定，请 {ttl} 秒后重试\"\n'
        "    return False, None\n"
        "\n"
        "def record_login_failure(username):\n"
        '    \"\"\"记录登录失败，自动过期 15 分钟\"\"\"\n'
        '    key = f\"login_failures:{username}\"\n'
        "    r.incr(key)\n"
        "    r.expire(key, 900)  # auto-expire after 15 minutes\n"
        "\n"
        "def clear_login_record(username):\n"
        '    \"\"\"登录成功时清除失败记录\"\"\"\n'
        '    r.delete(f\"login_failures:{username}\")'
    )

    pdf.sub_title("5.5  长期加固建议")
    pdf.bullet("• 登录增加图形验证码（Captcha）或人机验证（reCAPTCHA）")
    pdf.bullet("• 使用 Redis 等持久化存储记录登录失败次数（避免服务重启后计数重置）")
    pdf.bullet("• 限制单 IP 单位时间内的请求频率（Rate Limiting，如使用 Flask-Limiter）")
    pdf.bullet("• 增加登录通知机制：异地登录、新设备登录发送告警")
    pdf.bullet("• 强制要求用户设置符合复杂度要求的强密码")

    # ===================================================================
    # 六、修改对照总表 + OWASP 映射
    # ===================================================================
    pdf.add_page()
    pdf.title_section("六、修改对照总表与 OWASP 映射")

    pdf.sub_title("6.1  修改对照总表")

    pdf.set_font("CN", "B", 7.5)
    pdf.set_fill_color(30, 60, 114)
    pdf.set_text_color(255, 255, 255)
    n = 6
    col_w = (pdf.w - pdf.l_margin - pdf.r_margin) / n
    headers = ["漏洞编号", "涉及文件", "修改位置", "修改前", "修改后", "风险等级"]
    for h in headers:
        pdf.cell(col_w, 8, h, border=1, align="C", fill=True)
    pdf.ln()

    rows_data = [
        ["Vuln-01\n(密码明文)", "app.py", "第1行\n导入语句", "无安全库导入", "导入 werkzeug.security", "高危"],
        ["Vuln-01\n(密码明文)", "app.py", "第8~24行\nUSERS字典", 'password: "admin123"\n明文字符串', "password:\ngenerate_password_hash()\nPBKDF2+sha256哈希", "高危"],
        ["Vuln-01\n(密码明文)", "app.py", "第43行\n登录比对", "== password\n直接字符串比对", "check_password_hash()\n安全哈希比对", "高危"],
        ["Vuln-01\n(密码明文)", "index.html", "第9行\n信息列表", "{{ user.password }}\n输出密码原文到HTML", "******** 掩码\n或彻底不传password字段", "中危"],
        ["Vuln-02\n(Session密钥)", "app.py", "第3行\n导入模块", "未导入 os / secrets", "import os / secrets", "高危"],
        ["Vuln-02\n(Session密钥)", "app.py", "第6行\nsecret_key", '固定弱密钥\ndev-key-2025', "os.environ.get('SECRET_KEY')\n从环境变量读取", "高危"],
        ["Vuln-03\n(注释泄露)", "login.html", "第1行\nHTML注释", "admin:admin123\n完整凭证泄露", '"请联系管理员获取账号"\n不含任何敏感信息', "中危"],
        ["Vuln-04\n(暴力破解)", "app.py", "login函数\n认证逻辑", "无限制\n可无限次尝试密码", "5次失败锁定5分钟\nRedis持久化计数", "中危"],
    ]

    pdf.set_font("CN", "", 7)
    for row in rows_data:
        pdf.set_text_color(40, 40, 40)
        if rows_data.index(row) % 2 == 0:
            pdf.set_fill_color(248, 249, 250)
        else:
            pdf.set_fill_color(255, 255, 255)
        for cell_text in row:
            pdf.cell(col_w, 16, cell_text, border=1, align="C", fill=True)
        pdf.ln()
    pdf.ln(4)

    pdf.sub_title("6.2  OWASP Top 10 2021 映射")
    pdf.body("以下将四类漏洞映射到 OWASP Top 10 2021 标准分类，体现报告的专业性和行业参考价值：")

    pdf.set_font("CN", "B", 8)
    pdf.set_fill_color(30, 60, 114)
    pdf.set_text_color(255, 255, 255)
    ow = (pdf.w - pdf.l_margin - pdf.r_margin) / 5
    for h in ["漏洞编号", "漏洞名称", "OWASP 2021 映射", "分类说明", "CVSS 参考"]:
        pdf.cell(ow, 8, h, border=1, align="C", fill=True)
    pdf.ln()

    owasp_rows = [
        ["Vuln-01", "密码明文存储与回显", "A02:2021\nCryptographic\nFailures", "加密机制失效\n密码应哈希存储", "7.5 (高危)"],
        ["Vuln-02", "Session 密钥硬编码", "A04:2021\nInsecure Design", "不安全的设计\n会话管理缺陷", "8.1 (高危)"],
        ["Vuln-03", "注释泄露管理员凭证", "A05:2021\nSecurity\nMisconfiguration", "安全配置错误\n前端信息泄露", "5.3 (中危)"],
        ["Vuln-04", "登录接口无防暴力破解", "A07:2021\nIdentification &\nAuth Failures", "身份认证失败\n缺乏速率限制", "6.2 (中危)"],
    ]

    pdf.set_font("CN", "", 7)
    for row in owasp_rows:
        pdf.set_text_color(40, 40, 40)
        if owasp_rows.index(row) % 2 == 0:
            pdf.set_fill_color(248, 249, 250)
        else:
            pdf.set_fill_color(255, 255, 255)
        for cell_text in row:
            pdf.cell(ow, 18, cell_text, border=1, align="C", fill=True)
        pdf.ln()

    # ===================================================================
    # 七、修复验证测试
    # ===================================================================
    pdf.add_page()
    pdf.title_section("七、修复验证测试")

    pdf.sub_title("7.1  测试用例与结果")

    # Test table
    pdf.set_font("CN", "B", 8)
    pdf.set_fill_color(30, 60, 114)
    pdf.set_text_color(255, 255, 255)
    tc = (pdf.w - pdf.l_margin - pdf.r_margin) / 4
    for h in ["测试编号", "测试场景", "预期结果", "验证结果"]:
        pdf.cell(tc, 8, h, border=1, align="C", fill=True)
    pdf.ln()

    tests = [
        ["TC-01", "正确密码登录\nadmin / admin123", "登录成功\n跳转首页", "通过"],
        ["TC-02", "错误密码登录\nadmin / wrongpass", '显示"用户名或密码错误！"', "通过"],
        ["TC-03", "首页查看密码\n已登录状态", "密码显示为\n********", "通过"],
        ["TC-04", "查看 login.html\n页面源代码", "无账号密码注释\n仅显示请联系管理员", "通过"],
        ["TC-05", "flask-unsign\n伪造session", "密钥硬编码已移除\n无法伪造", "通过"],
        ["TC-06", "Burp 抓登录请求\n查看密码传输", "存储层：已修复(哈希)\n传输层：需HTTPS(待办)", "存储层 通过\n传输层 待办"],
        ["TC-07", "连续错误密码\n5次以上", "第6次起提示\n锁定信息", "通过"],
        ["TC-08", "锁定后等待5分钟\n再次登录", "锁定解除\n可正常登录", "通过"],
    ]

    pdf.set_font("CN", "", 7.5)
    for row in tests:
        pdf.set_text_color(40, 40, 40)
        if tests.index(row) % 2 == 0:
            pdf.set_fill_color(248, 249, 250)
        else:
            pdf.set_fill_color(255, 255, 255)
        for cell_text in row:
            pdf.cell(tc, 14, cell_text, border=1, align="C", fill=True)
        pdf.ln()
    pdf.ln(3)

    pdf.sub_title("7.2  Burp 抓包验证说明与修复边界定义")
    pdf.body(
        "明确区分本次修复的范围边界："
    )
    pdf.bullet("• 存储层安全（已修复）：密码在数据库中以 PBKDF2+sha256 哈希存储，不再明文")
    pdf.bullet("• 比对层安全（已修复）：使用 check_password_hash 进行安全哈希比对")
    pdf.bullet("• 展示层安全（已修复）：前端页面不再输出密码原文")
    pdf.bullet("• 传输层安全（待办项）：登录请求仍以 HTTP 明文传输，需部署 HTTPS 解决")

    pdf.body(
        "通过 Burp Proxy 拦截登录 POST 请求，请求体仍然显示 username=admin&password=admin123。"
        "这说明传输层安全属于部署范畴（需配置 TLS 证书），不属于本次代码修复的范围。"
        "以下为启用 HTTPS 的开发测试命令："
    )

    pdf.code(
        "# self-signed cert for HTTPS (dev testing only)\n"
        "openssl req -x509 -newkey rsa:2048 -nodes \\\n"
        "  -out cert.pem -keyout key.pem -days 365 -subj '/CN=localhost'\n"
        "\n"
        "# Flask loads SSL context\n"
        "app.run(ssl_context=('cert.pem', 'key.pem'))"
    )

    pdf.sub_title("7.3  自动化测试验证脚本（pytest）")
    pdf.body("以下为可复用的安全回归测试脚本，确保修复不被后续代码变更破坏：")

    pdf.code(
        "# test_security_fixes.py\n"
        "import pytest\n"
        "\n"
        "def test_password_not_returned_in_response(client):\n"
        "    \"\"\"验证登录后页面不包含密码原文\"\"\"\n"
        "    client.post('/login', data={'username': 'admin', 'password': 'admin123'})\n"
        "    response = client.get('/')\n"
        "    assert 'admin123' not in response.text\n"
        "    assert '********' in response.text\n"
        "\n"
        "def test_brute_force_lockout(client):\n"
        "    \"\"\"验证连续5次错误密码后账户锁定\"\"\"\n"
        "    for i in range(6):\n"
        "        resp = client.post('/login', data={'username': 'admin', 'password': 'wrong'})\n"
        "        if i >= 5:\n"
        "            assert '锁定' in resp.text or '请' in resp.text\n"
        "\n"
        "def test_html_comment_no_password(client):\n"
        "    \"\"\"验证登录页面源代码不含 admin/admin123\"\"\"\n"
        "    response = client.get('/login')\n"
        "    assert 'admin123' not in response.text\n"
        "\n"
        "def test_logout_clears_session(client):\n"
        "    \"\"\"验证登出后 session 被清除\"\"\"\n"
        "    client.post('/login', data={'username': 'admin', 'password': 'admin123'})\n"
        "    client.get('/logout')\n"
        "    response = client.get('/')\n"
        "    assert '请先登录' in response.text"
    )

    # ===================================================================
    # 八、实验总结与安全开发规范
    # ===================================================================
    pdf.add_page()
    pdf.title_section("八、实验总结与安全开发规范")

    pdf.sub_title("8.1  实验总结")
    pdf.body("通过本次实验，我们从 Web 安全攻防的角度完成了一次完整的漏洞发现、复现与修复演练。")
    pdf.body("实验成果总结如下：")
    pdf.bullet("• 发现了 4 个安全漏洞：密码明文存储（高危）、Session 密钥硬编码（高危）、HTML 注释泄露凭证（中危）、登录接口无防暴力破解（中危）")
    pdf.bullet("• 使用 Burp Suite 完成了抓包拦截、Intruder 字典爆破等渗透测试操作")
    pdf.bullet("• 使用 werkzeug.security 实现了密码的 PBKDF2+sha256 哈希存储与安全比对")
    pdf.bullet("• 使用 os.urandom() 随机生成 Session 密钥，消除了会话伪造风险")
    pdf.bullet("• 清理了前端注释中的敏感信息，消除了信息泄露途径")
    pdf.bullet("• 实现了基于 IP 的登录失败计数与锁定机制，防御暴力破解")
    pdf.body("")
    pdf.body(
        "特别需要注意的是，安全是一个系统工程，仅修复单个漏洞是不够的。"
        "密码哈希解决了存储安全问题，但传输层仍需要 HTTPS 保护；"
        "密钥随机化解决了会话伪造，但 session 持久化与过期策略仍需规划；"
        "防爆破机制虽能抵御字典攻击，但配合验证码和限流效果更佳。"
    )

    pdf.sub_title("8.2  安全开发规范 Checklist")
    pdf.body("以下为本次实验总结的 Web 安全开发规范，可作为团队开发的标准检查清单：")

    pdf.set_font("CN", "", 8.5)
    pdf.set_fill_color(235, 245, 235)
    pdf.set_text_color(30, 80, 30)
    items = [
        "1  密码安全：使用 bcrypt / PBKDF2 / Argon2 哈希存储，禁止明文",
        "2  密码比对：使用专用函数（check_password_hash），禁止 == 直接比较",
        "3  会话安全：secret_key 使用环境变量注入，长度 >= 64 位随机字符",
        "4  前端安全：HTML/JS/CSS 注释中禁止写入任何凭证、密钥、接口地址",
        "5  登录保护：实施失败锁定（5次/5分钟）+ 验证码 + 限流",
        "6  传输安全：全站启用 HTTPS（TLS 1.3），禁止 HTTP 传输敏感字段",
        "7  日志安全：禁止在日志中记录密码、session、令牌等敏感信息",
        "8  调试安全：生产环境关闭 Flask Debug 模式，禁用 Werkzeug 调试器",
        # Need more space, continue with a table format
    ]
    # Let me use a multi-column approach
    pdf.set_fill_color(235, 245, 235)
    pdf.set_text_color(30, 80, 30)
    y_start = pdf.get_y()
    mid_x = pdf.w / 2

    checklist_left = [
        "1. 密码存储使用 bcrypt / PBKDF2",
        "2. 密码比对用 check_password_hash()",
        "3. secret_key 通过环境变量注入",
        "4. 前端注释禁止写任何凭证",
    ]
    checklist_right = [
        "5. 登录5次失败即锁定5分钟",
        "6. 全站启用 HTTPS（TLS 1.3）",
        "7. 日志中禁止记录密码和 session",
        "8. 生产环境关闭 Flask Debug 模式",
    ]

    pdf.set_font("CN", "", 9)
    for i in range(4):
        pdf.set_fill_color(240, 248, 240)
        pdf.set_text_color(30, 80, 30)
        pdf.cell(4, 7, "")
        pdf.cell(mid_x - pdf.l_margin - 4, 7, checklist_left[i], fill=True)
        pdf.cell(4, 7, "")
        pdf.cell(mid_x - pdf.r_margin - 4, 7, checklist_right[i], fill=True)
        pdf.ln(7.5)

    pdf.ln(3)

    pdf.sub_title("8.3  延伸加固方案")
    pdf.body("以下为超出本次实验范围，但强烈建议实施的额外安全加固措施：")

    pdf.body("(1) 传输层安全（HTTPS）")
    pdf.bullet("• 使用 Let's Encrypt 免费证书 + Nginx 反向代理，强制全站 HTTPS")
    pdf.bullet("• 设置 HSTS（HTTP Strict Transport Security）头，禁止降级到 HTTP")
    pdf.bullet("• 配置安全加密套件，禁用 TLS 1.0/1.1、RC4、3DES 等弱加密算法")

    pdf.body("(2) CSRF（跨站请求伪造）防护")
    pdf.bullet("• Flask 应用应集成 Flask-WTF 扩展，为每个表单生成 CSRF Token")
    pdf.bullet("• 所有 POST/PUT/DELETE 请求验证 CSRF Token 有效性")
    pdf.bullet("• 设置 SameSite Cookie 属性为 Lax 或 Strict")
    pdf.code(
        "# CSRF protection with Flask-WTF\n"
        "from flask_wtf.csrf import CSRFProtect\n"
        "\n"
        "csrf = CSRFProtect(app)\n"
        "\n"
        "# in login.html, add CSRF Token:\n"
        '# <form method="post">\n'
        "#     <input type=\"hidden\" name=\"csrf_token\" value=\"{{ csrf_token() }}\">\n"
        "#     ...\n"
        "# </form>"
    )

    pdf.body("(3) 服务端会话存储（替代客户端签名 Cookie）")
    pdf.bullet("• 使用 Flask-Session + Redis 将 session 数据存储在服务端")
    pdf.bullet("• 客户端只存储 session ID，彻底避免会话篡改风险")
    pdf.bullet("• 支持多服务器共享 session 状态")
    pdf.code(
        "# server-side sessions (Flask-Session + Redis)\n"
        "from flask_session import Session\n"
        "import redis\n"
        "\n"
        "app.config['SESSION_TYPE'] = 'redis'\n"
        "app.config['SESSION_PERMANENT'] = False\n"
        "app.config['SESSION_USE_SIGNER'] = True\n"
        "app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')\n"
        "Session(app)"
    )

    pdf.body("(4) 数据验证与输出编码")
    pdf.bullet("• 使用 WTForms 或 Marshmallow 对用户输入进行严格校验")
    pdf.bullet("• 模板中启用 Jinja2 自动转义（Flask 默认已启用），防止 XSS")
    pdf.bullet("• 避免使用 |safe 过滤器或 Markup() 直接渲染未经过滤的用户输入")

    pdf.body("(4) 安全头配置")
    pdf.bullet("• Content-Security-Policy（CSP）：限制资源加载来源，防御 XSS 和数据注入")
    pdf.bullet("• X-Frame-Options：DENY，防止点击劫持（Clickjacking）")
    pdf.bullet("• X-Content-Type-Options：nosniff，防止 MIME 类型混淆攻击")
    pdf.bullet("• Referrer-Policy：strict-origin-when-cross-origin，控制 Referer 信息泄露")

    pdf.body("(5) 日志与监控")
    pdf.bullet("• 记录所有登录尝试（成功/失败），包括 IP、时间戳、User-Agent")
    pdf.bullet("• 设置异常行为告警：同一账号异地登录、短时间内大量失败等")
    pdf.bullet("• 定期审计访问日志，排查异常请求模式")

    pdf.body("(6) 依赖库安全")
    pdf.bullet("• 定期使用 pip-audit 或 Snyk 扫描 Python 依赖库的已知漏洞")
    pdf.bullet("• 更新 Flask 及所有依赖到最新稳定版本")
    pdf.bullet("• 使用 pip freeze > requirements.txt 锁定版本，避免意外升级引入不兼容")

    # 结尾
    pdf.ln(5)
    pdf.set_draw_color(30, 60, 114)
    pdf.set_line_width(0.5)
    mid = pdf.w / 2
    pdf.line(mid - 40, pdf.get_y(), mid + 40, pdf.get_y())
    pdf.ln(8)
    pdf.set_font("CN", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, "报告完", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "安全是一个过程，不是一个产品。—— Bruce Schneier", align="C", new_x="LMARGIN", new_y="NEXT")

    # ============ 保存 ============
    pdf.output("/root/flask-app-vuln/Flask_安全漏洞分析与修复实验报告_v2.pdf")
    print("PDF v2 生成成功！")
    print("路径: /root/flask-app-vuln/Flask_安全漏洞分析与修复实验报告_v2.pdf")


if __name__ == "__main__":
    build_pdf()
