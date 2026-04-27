# iCloud to Google Drive 迁移工具

一个运行在 **Windows** 本地的命令行工具，将 iCloud Drive 中的文件批量迁移到 Google Drive，并生成带哈希校验的完整迁移证据报告。

**特点：**
- 自动识别并跳过尚未下载到本地的 iCloud 占位文件（无需手动等待同步）
- 每个文件上传后用 SHA-256 / MD5 双重校验，确保数据完整性
- 断点续传：程序中断后重新运行会自动跳过已成功迁移的文件
- 导出 JSON / CSV 格式的迁移清单，便于溯源和归档
- **不会自动删除任何 iCloud 文件**，清理须手动操作

---

## 前置步骤

在运行迁移工具之前，需要完成以下两项配置。

### 1. 安装并配置 Windows iCloud 客户端

1. 在 Windows 上前往 Microsoft Store 搜索 **iCloud**，或直接访问 [Apple iCloud for Windows](https://support.apple.com/en-us/103232) 下载安装。
2. 安装完成后，使用您的 Apple ID 登录。
3. 在 iCloud 设置中勾选 **iCloud Drive**，等待同步初始化完成。
4. 确认在文件资源管理器中能看到 `iCloud Drive` 目录（默认路径为 `C:\Users\<你的用户名>\iCloudDrive`）。

> [!NOTE]
> iCloud Drive 目录中的文件可能以"占位符"（Shell Link）形式存在，图标带有云朵标志，文件实际内容尚未下载到本地。本工具会自动识别并跳过这些文件，在迁移报告中以 `SOURCE_PLACEHOLDER` 状态记录它们。
>
> 如果您希望迁移这些文件，需先在 iCloud 设置中选择"始终保存在此设备"，等待对应文件下载完成后再运行迁移工具。

---

### 2. 获取 Google Drive API 凭据（client_secret.json）

工具使用 OAuth 2.0 授权访问您的 Google Drive，需要一个 `client_secret.json` 文件。以下是获取步骤：

1. **创建 GCP 项目**
   - 打开 [Google Cloud Console](https://console.cloud.google.com/)，登录您的 Google 账号。
   - 点击顶部项目选择器 > **新建项目**，命名为 `iCloud-to-Gdrive`（或任意名称），然后创建。

2. **启用 Google Drive API**
   - 进入 **API 和服务 > 库**，搜索 `Google Drive API`，点击启用。

3. **配置 OAuth 同意屏幕**
   - 进入 **API 和服务 > OAuth 同意屏幕**。
   - 用户类型选 **外部**，点击创建。
   - 填写应用名称（如 `iCloud-to-Gdrive`），支持邮箱和开发者联系邮箱填写您自己的 Gmail。
   - 在 **测试用户** 步骤中，点击"添加用户"，添加您自己的 Gmail 地址。完成后保存。

4. **创建 OAuth 客户端 ID**
   - 进入 **API 和服务 > 凭据**。
   - 点击 **+ 创建凭据 > OAuth 客户端 ID**。
   - 应用类型选 **桌面应用**，名称填 `Migration Script`，点击创建。
   - 在弹出的对话框中点击 **下载 JSON**。

5. **放置凭据文件**
   - 将下载的 JSON 文件重命名为 `client_secret.json`，放在本项目的根目录下（与 `pyproject.toml` 同级）。

> [!WARNING]
> `client_secret.json` 包含私密信息，请勿提交到 Git 仓库。项目的 `.gitignore` 已经配置好了对该文件的排除规则。

---

## 安装

本项目使用 [uv](https://github.com/astral-sh/uv) 管理依赖。

```bash
# 克隆仓库
git clone https://github.com/goldengrape/iCloud-to-Gdrive.git
cd iCloud-to-Gdrive

# 安装依赖（uv 会自动创建虚拟环境）
uv sync
```

---

## 使用方法

### 首次运行（需要授权）

第一次运行时，程序会自动打开浏览器，引导您登录 Google 账号并授权访问 Google Drive。授权完成后，Token 会被安全保存到 Windows 凭据管理器中，后续运行无需再次授权。

```bash
uv run icloud-to-gdrive migrate
```

### 常用参数

```bash
uv run icloud-to-gdrive migrate [选项]

选项：
  --source <路径>         iCloud Drive 的本地路径（默认：~\iCloudDrive）
  --client-secret <文件>  client_secret.json 文件路径（默认：client_secret.json）
  --db-path <文件>        迁移状态数据库路径（默认：migration.db）
```

**示例：**

```bash
# 使用默认路径运行
uv run icloud-to-gdrive migrate

# 指定自定义源目录
uv run icloud-to-gdrive migrate --source "C:\Users\YourName\iCloudDrive"

# 指定数据库路径（便于多次迁移任务区分归档）
uv run icloud-to-gdrive migrate --db-path my_migration_2026.db
```

### 断点续传

程序支持安全中断。随时按 `Ctrl+C` 暂停后，下次运行同样命令，程序会自动跳过已成功验证（`VERIFIED_MATCH`）的文件，从未完成的位置继续迁移。

### 迁移结果

迁移完成后，程序会在当前目录生成两个报告文件：

| 文件 | 说明 |
|---|---|
| `manifest_<时间戳>.json` | 完整迁移记录（含每个文件的来源路径、目标 Drive 文件 ID、MD5/SHA-256 哈希值、迁移状态） |
| `manifest_<时间戳>.csv` | 同上，表格格式，方便在 Excel 中查阅 |

> [!NOTE]
> `manifest.json` 和 `migration.db` 包含您的文件路径等个人信息，**请不要将其提交到 GitHub**。这两类文件已被 `.gitignore` 排除。

---

## 运行测试

```bash
uv run pytest tests/
```

---

## 项目文档

| 文档 | 说明 |
|---|---|
| `docs/URD.md` | 用户需求文档 |
| `docs/ADD.md` | 架构设计文档 |
| `docs/MDD.md` | 模块设计文档 |
| `docs/TDD.md` | 测试计划文档 |
| `docs/RMD.md` | 开发路线与任务记录 |
| `docs/TRACE.md` | 需求追踪矩阵 |
| `docs/agent_guide_gcp_oauth.md` | AI 代理协助获取 OAuth 凭据的操作指引 |

---

## 安全说明

- 本工具**不会收集 Apple ID 密码**，亦不调用任何 iCloud 私有 API。
- Google 账号仅通过官方 OAuth 2.0 流程授权，Token 加密保存在 Windows 凭据管理器中。
- **本工具不会自动删除任何文件**。迁移完成后是否清理 iCloud 中的源文件，完全由您手动决定。
