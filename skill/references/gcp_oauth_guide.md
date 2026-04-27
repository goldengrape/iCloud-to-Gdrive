# GCP OAuth 凭据配置指引

本文档供 AI agent 使用，包含为 iCloud-to-Gdrive 配置 Google OAuth 凭据的完整流程。

---

## 方式一：browser_subagent 自动化（推荐）

如果 AI agent 具备 `browser_subagent` 工具，将以下内容作为 Task 传给它：

```text
Navigate to Google Cloud Console (https://console.cloud.google.com/) and create OAuth credentials for a Desktop App.

Detailed steps:
1. If not logged in, stop and report failure. (Assume already logged in to Google).
2. Create a new project named "iCloud GDrive Transfer", or use an existing project. Accept terms of service if prompted.
3. Go to APIs & Services > Library. Search for "Google Drive API" and click Enable.
4. Go to APIs & Services > OAuth consent screen.
   - Select "External" and click Create.
   - App name: "iCloud-to-Gdrive"
   - Support email: select the current user's email from the dropdown.
   - Developer contact email: use the current user's email.
   - Click Save and Continue through all steps.
   - In "Test users", click "ADD USERS", add the current user's email. Click Add, then Save and Continue.
5. Go to APIs & Services > Credentials.
   - Click "+ CREATE CREDENTIALS" > "OAuth client ID".
   - Application type: Desktop app. Name: "Migration Script".
   - Click Create.
6. In the dialog that appears, click "Download JSON".
7. Return the absolute path to the downloaded JSON file, OR the exact raw JSON content.
```

**browser_subagent 返回后：**

1. 将 JSON 内容保存为 `client_secret.json`：
```powershell
# 如果 subagent 返回了下载路径，执行复制
Copy-Item "C:\Users\golde\Downloads\client_secret_*.json" "c:\Users\golde\code\iCloud-to-Gdrive\client_secret.json"
```

2. 验证 `.gitignore` 已排除该文件：
```powershell
Select-String "client_secret" "c:\Users\golde\code\iCloud-to-Gdrive\.gitignore"
```

3. 告知用户凭据配置完成，可以运行迁移命令。

---

## 方式二：用户手动配置

若自动化失败，引导用户按以下步骤手动操作：

1. 打开 [Google Cloud Console](https://console.cloud.google.com/)，登录 Google 账号
2. 新建项目（名称任意）> 进入 **API 和服务 > 库** > 搜索启用 **Google Drive API**
3. 进入 **OAuth 同意屏幕**：
   - 用户类型选"外部"
   - 填写应用名称和联系邮箱
   - 在"测试用户"中添加自己的 Gmail 地址
4. 进入 **凭据 > 创建凭据 > OAuth 客户端 ID**：
   - 应用类型：桌面应用
   - 点击创建，然后点击"下载 JSON"
5. 将下载的文件重命名为 `client_secret.json`，放到项目根目录（与 `pyproject.toml` 同级）

---

## 验证配置成功

```powershell
Test-Path "c:\Users\golde\code\iCloud-to-Gdrive\client_secret.json"
# 应返回 True
```
