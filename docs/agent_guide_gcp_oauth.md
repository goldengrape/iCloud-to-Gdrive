# AI 代理操作指引：如何协助用户获取 Google OAuth Client Secret

这份文档是专门为 AI Agent（如 Antigravity 及其 `browser_subagent`）准备的标准操作程序（SOP）。
当项目需要配置真实的 Google Drive API 访问权限，而用户尚未提供 `client_secret.json` 且需要 AI 协助时，AI 应该按照以下流程自动化（或半自动化）获取凭据。

## 前提条件

1. **用户已登录 Google 账号**：AI 调用的浏览器会话需要已经具备 Google 的登录态。
2. **具备浏览器控制工具**：Agent 需要具备如 `browser_subagent` 等能够自动操作用户本地浏览器的工具。

## 自动化执行步骤 (Subagent Task 模版)

作为 AI 助手，你可以直接将以下 `Task` 描述文案传递给你的浏览器自动化子代理（如 `browser_subagent`），以确保它具备最高效且明确的执行上下文：

```text
Navigate to Google Cloud Console (https://console.cloud.google.com/) and create OAuth credentials for a Desktop App. 
Detailed steps:
1. If not logged in, ask the user to log in or fail the task. (Assuming already logged in to Google).
2. Create a new project (e.g., "iCloud GDrive Transfer") or use an existing one. If you see terms of service, accept them.
3. Go to APIs & Services > Library. Search for "Google Drive API" and click "Enable".
4. Go to APIs & Services > OAuth consent screen. 
   - Select "External" and click Create.
   - App name: "iCloud-to-Gdrive"
   - Support email: select the current user's email from the dropdown.
   - Developer contact email: use the current user's email.
   - Click Save and Continue.
   - Skip Scopes (click Save and Continue).
   - In "Test users", click "ADD USERS" and type the current user's email address. Click Add. Then Save and Continue.
5. Go to APIs & Services > Credentials.
   - Click "+ CREATE CREDENTIALS" at the top and select "OAuth client ID".
   - Application type: select "Desktop app". Name: "Migration Script".
   - Click "Create".
6. In the dialog that appears, click the "Download JSON" button.
7. Once downloaded, find the downloaded file's path (usually in the user's Downloads folder) OR read the raw JSON content from the screen if possible.
8. Your final return MUST contain either the absolute path to the downloaded JSON file OR the exact JSON string of the client secret so the parent agent can save it to the workspace.
```

## 执行后动作 (父级 Agent 职责)

当浏览器自动化工具（Subagent）成功返回了 JSON 文件的纯文本内容或其本地下载路径后：
1. **保存或转移文件**：AI 需要将 JSON 文本直接写入，或将下载的文件转移到工作区根目录下的 `client_secret.json` 中（即项目根目录）。
2. **安全核对**：核实项目中的 `.gitignore` 文件，确保其中包含 `client_secret.json`，防止该机密文件被提交到 GitHub 等版本控制系统。
3. **通知用户**：以友好的方式告知用户整个繁琐的申请流程已在后台自动化完成，并且告知他们现在可以直接运行后续的端到端身份验证脚本了（例如 `uv run python tests/e2e_auth_test.py`）。
