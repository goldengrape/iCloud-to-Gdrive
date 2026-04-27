---
name: icloud-to-gdrive
description: 将 Windows 本地 iCloud Drive 中的文件迁移到 Google Drive，自动跳过云端占位符文件，上传后进行 SHA-256/MD5 哈希校验，生成可溯源的迁移证据报告。使用场景：用户要求迁移 iCloud 文件到 Google Drive、要求安装或配置本工具、要求配置 Google OAuth 凭据（client_secret.json）、要求查看迁移进度或验证迁移结果。工具仓库路径：c:\Users\golde\code\iCloud-to-Gdrive
---

# iCloud to Google Drive 迁移工具

**工作目录：** `c:\Users\golde\code\iCloud-to-Gdrive`  
**运行环境：** Windows + PowerShell + uv

---

## 工作流一：安装工具

如果用户尚未安装此工具，按以下步骤完成：

```powershell
# 1. 克隆仓库（如果尚未克隆）
git clone https://github.com/goldengrape/iCloud-to-Gdrive.git
cd iCloud-to-Gdrive

# 2. 安装依赖（uv 会自动创建虚拟环境）
uv sync
```

安装完成后，运行 `uv run icloud-to-gdrive --help` 验证安装成功。

---

## 工作流二：配置 Google OAuth 凭据

**触发条件：** 项目根目录不存在 `client_secret.json` 时。

检查凭据是否存在：
```powershell
Test-Path "c:\Users\golde\code\iCloud-to-Gdrive\client_secret.json"
```

若返回 `False`，请阅读 [references/gcp_oauth_guide.md](references/gcp_oauth_guide.md)，其中包含可直接传给 `browser_subagent` 的自动化任务模版，以及手动配置的详细步骤。

---

## 工作流三：执行迁移

### 前置条件确认

1. Windows iCloud 客户端已安装并登录（目录 `~\iCloudDrive` 存在）
2. `client_secret.json` 已配置（参见工作流二）

### 运行命令

```powershell
cd c:\Users\golde\code\iCloud-to-Gdrive
uv run icloud-to-gdrive migrate
```

**可选参数：**

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--source` | `~\iCloudDrive` | iCloud Drive 本地路径 |
| `--client-secret` | `client_secret.json` | OAuth 凭据文件路径 |
| `--db-path` | `migration.db` | 迁移状态数据库路径 |

### 首次运行

首次运行会打开浏览器请求 Google 授权，用户完成后程序自动继续。Token 保存在 Windows 凭据管理器，后续无需重授权。

### 断点续传

中断后重新运行同一命令，自动跳过已校验成功（`VERIFIED_MATCH`）的文件。

### 解读输出，向用户汇报

| 输出关键字 | 含义 |
|---|---|
| `Successfully verified <文件名>` | 上传并校验成功 |
| `Skipped placeholder: <路径>` | 文件在 iCloud 云端未下载，已跳过 |
| `Upload failed` | 上传失败，需关注 |
| `Verification failed` | 校验不通过，需关注 |
| `manifest_<时间戳>.json` | 最终证据报告路径 |

---

## 工作流四：验证迁移结果

迁移完成后，工作目录生成：
- `manifest_<时间戳>.json`：完整迁移记录（含哈希值、Drive 文件 ID）
- `manifest_<时间戳>.csv`：表格格式

向用户汇报时，关注：
1. `VERIFIED_MATCH` 数量（成功）vs `SOURCE_PLACEHOLDER` 数量（跳过，文件未下载）
2. `FAILED_*` 状态的条目及其 `failure_reason`
3. 报告末行输出的整体 SHA-256（迁移证据的指纹）

---

## 常见问题

| 现象 | 处理方式 |
|---|---|
| 大量 `Skipped placeholder` | 在 iCloud 设置中选择"始终保存在此设备"，等待下载后重新运行 |
| `client_secret.json not found` | 执行工作流二配置凭据 |
| Token 过期 / 认证失败 | 重新运行，程序会触发浏览器重新授权 |
| `Upload failed: quota` | 用户 Google Drive 空间不足 |

---

## 安全提醒

- 本工具**不会删除任何 iCloud 文件**
- `client_secret.json`、`migration.db`、`manifest_*.json/csv` 均含私人信息，**不得提交 Git**（`.gitignore` 已排除）
- OAuth Token 保存在 Windows 凭据管理器，不以明文存储于磁盘
