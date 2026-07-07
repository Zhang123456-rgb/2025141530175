#!/usr/bin/env python3
"""Replace Chinese text in code blocks with English for PDF rendering with DejaVuSansMono"""
import re

with open('/root/flask-app-vuln/generate_report_v2.py', 'r') as f:
    content = f.read()

# Define replacements - order matters (longer matches first)
replacements = [
    # Block 1: Project structure
    ('# Flask主应用（路由、用户数据库、登录逻辑）', '# main app (routes, user DB, login logic)'),
    ('# 基础模板（导航栏、布局）', '# base template (navbar, layout)'),
    ('# 首页（用户信息展示）', '# home page (user info display)'),
    ('# 登录页', '# login page'),
    ('# 全局样式', '# global styles'),
    ('初始版本故意留有 4 个安全漏洞用于教学实验，以下逐一分析、复现并修复。', ''),  # This is body text, not code, skip

    # Block 2: index.html fix
    ('<!-- templates/index.html 修复前（漏洞行） -->', '<!-- BEFORE (vulnerable line) -->'),
    ('<!-- templates/index.html 修复后 -->', '<!-- AFTER (fixed) -->'),
    ('<!-- 更安全的做法：完全不渲染 password 字段 -->', '<!-- BEST: dont render password field at all -->'),
    ('<!-- 在 app.py 中构建传递给模板的字典时排除 password -->', '<!-- exclude password from dict passed to template -->'),

    # Block 3: flask-unsign decode
    ('# 解签 session cookie', '# decode session cookie'),
    ('# 如果已知密钥为 dev-key-2025，用其进行解签验证', '# if secret key is known, verify by unsigning'),

    # Block 4: flask-unsign forge
    ('# 伪造任意用户的 session', '# forge session for any user'),

    # Block 5: secret key fix
    ('# 修复后的正确做法', '# CORRECT approach (production)'),
    ('# 仅开发环境允许默认值，打印醒目警告', '# dev only: allow default with prominent warning'),

    # Block 6: Vuln 3 code block (before fix comment)
    ('<!-- 调试信息 - 默认管理员账号 用户名: admin 密码: admin123 -->', '<!-- DEBUG - default admin account: admin / admin123 -->'),

    # Block 7: Vuln 3 fix
    ('<!-- 修复前 -->', '<!-- BEFORE (vulnerable) -->'),
    ('<!-- 调试信息 - 默认管理员账号 用户名: admin 密码: admin123 -->', '<!-- DEBUG - default admin account: admin / admin123 -->'),
    ('<!-- 修复后 -->', '<!-- AFTER (fixed) -->'),
    ('<!-- 调试信息 - 请联系管理员获取账号 -->', '<!-- DEBUG - contact admin for credentials -->'),

    # Block 9: Memory counter
    ('# 方案一：内存计数器（本地开发用）', '# Option 1: in-memory counter (dev only)'),
    ('# 检查是否被锁定', '# check if locked'),
    ('# 登录成功，清除失败记录', '# login OK, clear failure record'),
    ('# 登录失败，增加计数', '# login failed, increment counter'),

    # Block 10: Redis counter
    ('# 方案二：Redis 持久化存储（生产环境推荐）', '# Option 2: Redis persistent storage (production)'),
    ('"""检查账号是否被锁定，返回 (是否锁定, 提示信息)"""', '"""check if account is locked, returns (is_locked, message)"""'),
    ('"""记录登录失败，自动过期 15 分钟"""', '"""record login failure, auto-expire in 15 min"""'),
    ('"""登录成功时清除失败记录"""', '"""clear failure record on successful login"""'),
    ('# 15分钟自动过期', '# auto-expire after 15 minutes'),

    # Block 11: HTTPS cert
    ('# 使用自签名证书启用 HTTPS（开发测试）', '# self-signed cert for HTTPS (dev testing only)'),
    ('# Flask 启动时加载 SSL 上下文', '# Flask loads SSL context'),

    # Block 12: pytest
    ('"""验证登录后页面不包含密码原文"""', '"""verify password plaintext not in response"""'),
    ('"""验证连续5次错误密码后账户锁定"""', '"""verify account locks after 5 wrong attempts"""'),
    ('"""验证登录页面源代码不含 admin/admin123"""', '"""verify login page source has no admin/admin123"""'),
    ('"""验证登出后 session 被清除"""', '"""verify session cleared after logout"""'),

    # Block 13: CSRF
    ('# CSRF 防护集成（Flask-WTF）', '# CSRF protection with Flask-WTF'),
    ('# 在 login.html 表单中添加 CSRF Token：', '# in login.html, add CSRF Token:'),

    # Block 14: Flask-Session
    ('# 服务端会话存储（Flask-Session + Redis）', '# server-side sessions (Flask-Session + Redis)'),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"Replaced: {old[:40]}...")
    else:
        print(f"NOT FOUND: {old[:40]}...")

with open('/root/flask-app-vuln/generate_report_v2.py', 'w') as f:
    f.write(content)

print("\nDone! All Chinese in code blocks replaced.")
