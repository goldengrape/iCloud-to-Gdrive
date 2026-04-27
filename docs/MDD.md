# MDD - Building Blocks / 模块设计文档

本文只定义模块、接口、数据结构和契约，不重复 URD 背景说明。

## 1. 模块列表

### MDD-MOD-001 PlatformDetector

职责：检测运行平台、iCloud Drive / iCloud Photos 可用状态、Google Drive 配置状态。

输入：系统环境、配置文件。  
输出：`PlatformCapabilities`。

> **当前状态（Phase 1）**：仅有 Mock 数据模型。
> **规划状态（Phase 2）**：将实现真实的 Windows 平台检测逻辑。

### MDD-MOD-002 ICloudDriveSourceAdapter

职责：按平台枚举和读取 iCloud Drive 文件。

- **macOS (Phase 3)**：通过系统文件访问能力读取 iCloud Drive；必须协调读取 package 和普通文件。
- **Windows (Phase 2 - RealWindowsICloudDriveAdapter)**：使用 `os` 或 `pathlib` 真实遍历 `~\iCloudDrive` 等本地物理目录；利用文件属性探测功能准确识别未下载的 `.iCloud` 文件，对未下载文件输出 `SOURCE_PLACEHOLDER` 并跳过处理。

> **当前状态（Phase 1）**：仅存在 `MockWindowsICloudAdapter` 等桩代码。

### MDD-MOD-003 ICloudPhotosSourceAdapter

职责：读取照片和视频资产。

- **macOS (Phase 3)**：PhotoKit 模式，输出资产资源与库级元数据。
- **Windows (Phase 2 - RealWindowsPhotosAdapter)**：目录模式，扫描 `~\Pictures\iCloud Photos` 目录输出普通媒体文件。

> **当前状态（Phase 1）**：仅存在 `MockMacPhotosAdapter` 等桩代码。

### MDD-MOD-004 ResourceNormalizer

职责：把文件、package、Live Photo、RAW+JPEG、sidecar 转换为统一 `TransferItem` 和 `ResourceGroup`。

### MDD-MOD-005 GoogleDriveTargetAdapter

职责：OAuth、目标目录管理、文件上传、目标元数据读取、Drive 错误分类。
> **规划实现 (RealGoogleDriveTargetAdapter)**：引入 `google-auth-oauthlib` 真实拉起浏览器授权，引入 `google-api-python-client` 真实调用 API 并实现 `Resumable Upload`。当前仅为 `MockGoogleDriveAdapter`。

### MDD-MOD-006 VerificationEngine

职责：源端 MD5/SHA-256 流式计算、目标 metadata 获取、校验结果判定。

### MDD-MOD-007 TaskStore

职责：用 SQLite 持久化任务状态、resumable session、offset、重试次数和 manifest 草稿。

### MDD-MOD-008 RetryScheduler

职责：执行带随机抖动的指数退避，处理 403、429、5xx、session 过期、配额暂停。

### MDD-MOD-009 ManifestWriter

职责：生成 JSON manifest、CSV 导出、文件级 record hash、整体 manifest SHA-256。`manifest_sha256` 必须能被独立验证；若写在 JSON 内，计算时必须排除 `metadata.manifest_sha256` 字段并使用 canonical JSON。

### MDD-MOD-010 CleanupAdvisor

职责：复核目标端仍存在，展示复核通过的已验证迁移列表和手动清理指引。复核失败项必须单独列为风险提示，不得混入清理候选。不得执行删除。

### MDD-MOD-011 SecurityBoundary

职责：OAuth token 安全存储、日志脱敏、凭据禁入检查。
> **规划实现**：在 Windows 上应调用 Credential Manager 等系统级安全存储，替代目前的 `DummyTokenStorage`。

### MDD-MOD-012 CLIRunner (新增)

职责：接收用户的命令行参数或交互式输入，初始化相关的 Adapter 和 TaskStore，调用 VerificationEngine 并报告上传进度，协调以上所有模块组装成可执行应用。
依赖：`argparse` / `click`，所有其他业务模块。

## 2. 数据结构

### MDD-DATA-001 PlatformCapabilities

```json
{
  "os": "macos | windows",
  "icloud_drive_available": true,
  "icloud_photos_available": true,
  "photos_mode": "photokit | directory | unavailable",
  "drive_mode": "coordinated_files | windows_cloud_files | unavailable",
  "limitations": ["string"]
}
```

### MDD-DATA-002 TransferItem

```json
{
  "task_id": "string",
  "record_id": "string",
  "source_type": "icloud_drive | icloud_photos",
  "source_stable_id": "string | null",
  "source_path": "string | null",
  "source_display_name": "string",
  "resource_group_id": "string | null",
  "resource_kind": "file | package_zip | photo | video | live_photo_still | live_photo_video | raw | sidecar",
  "source_size": 0,
  "source_mtime": "RFC3339 | null",
  "mime_type": "string | null"
}
```

### MDD-DATA-003 DriveUploadSession

```json
{
  "record_id": "string",
  "upload_session_uri": "string",
  "target_parent_folder_id": "string",
  "target_drive_file_id": "string | null",
  "confirmed_offset": 0,
  "session_created_at": "RFC3339",
  "last_checked_at": "RFC3339",
  "expires_at_estimate": "RFC3339 | null"
}
```

### MDD-DATA-004 ManifestRecord

```json
{
  "task_id": "string",
  "record_id": "string",
  "source_type": "icloud_drive | icloud_photos",
  "source_stable_id": "string | null",
  "source_path": "string | null",
  "source_display_name": "string",
  "source_size": 0,
  "source_mtime": "RFC3339 | null",
  "source_md5": "string | null",
  "source_sha256": "string | null",
  "resource_group_id": "string | null",
  "resource_kind": "string",
  "package_original_file_count": 0,
  "package_original_total_size": 0,
  "package_policy": "zip | expanded | plain | null",
  "package_contents_manifest_hash": "string | null",
  "target_drive_file_id": "string | null",
  "target_parent_folder_id": "string | null",
  "target_path": "string | null",
  "target_size": 0,
  "target_md5": "string | null",
  "target_sha1": "string | null",
  "target_sha256": "string | null",
  "target_head_revision_id": "string | null",
  "target_web_view_link": "string | null",
  "status": "MigrationStatus",
  "failure_reason": "string | null",
  "retry_count": 0,
  "started_at": "RFC3339 | null",
  "uploaded_at": "RFC3339 | null",
  "verified_at": "RFC3339 | null",
  "record_hash": "string"
}
```

### MDD-DATA-005 MigrationStatus

```text
PENDING
SOURCE_PLACEHOLDER
SOURCE_DOWNLOADING
SOURCE_UNAVAILABLE
PRECHECK_FAILED
TRANSFERRING
UPLOAD_PAUSED_RATE_LIMIT
UPLOAD_PAUSED_QUOTA
UPLOADED_UNVERIFIED
VERIFIED_MATCH
VERIFIED_WEAK
VERIFIED_SIZE_MISMATCH
VERIFIED_HASH_MISMATCH
CONFLICT_TARGET_EXISTS
SKIPPED_ALREADY_EXISTS
SKIPPED_BY_USER
FAILED_PERMISSION
FAILED_SOURCE_READ
FAILED_UPLOAD
FAILED_TARGET_VERIFY
FAILED_UNKNOWN
```

## 3. 接口契约

### MDD-API-001 SourceAdapter.list_items

```text
Input: SourceSelection
Output: Iterator<TransferItem | SourceEvent>
Preconditions:
- 用户已授予本地文件或照片访问权限。
- 适配器不得要求 Apple ID 密码。
Postconditions:
- 每个可迁移资源有稳定 record_id。
- 不可读资源也必须输出状态事件，不得静默丢弃。
Side effects:
- macOS 可能触发 iCloud 文件下载请求。
```

### MDD-API-002 SourceAdapter.open_stream

```text
Input: record_id
Output: readable byte stream + metadata snapshot
Preconditions:
- item 状态不是 SOURCE_UNAVAILABLE。
Postconditions:
- 返回的 metadata snapshot 可写入 manifest。
- 流读取过程可同时交给 VerificationEngine 计算哈希。
Side effects:
- 可能触发文件下载、文件协调等待或权限弹窗。
```

### MDD-API-003 GoogleDriveTargetAdapter.upload

```text
Input: TransferItem, byte stream, upload policy
Output: DriveUploadResult
Preconditions:
- OAuth token 有效或可刷新。
- 目标目录已授权。
Postconditions:
- 成功时返回 target_drive_file_id 和可用 metadata。
- 中断时返回 confirmed_offset 或可查询 session 状态。
Side effects:
- 在 Google Drive 中创建或更新文件。
```

### MDD-API-004 VerificationEngine.verify

```text
Input: SourceDigest, DriveFileMetadata
Output: VerificationResult
Rules:
- target_sha256 可用时优先比对 SHA-256。
- target_sha256 不可用但 target_md5 可用时比对 MD5。
- checksum 均不可用时不得输出 VERIFIED_MATCH，只能输出 VERIFIED_WEAK 或失败状态。
```

### MDD-API-005 ManifestWriter.finalize

```text
Input: ManifestRecord[]
Output: manifest.json, manifest.csv, manifest_sha256 或 manifest.json.sha256
Preconditions:
- 所有记录必须有 status。
Postconditions:
- JSON 包含 manifest metadata、records、record_hash。
- 若 `manifest_sha256` 写入 JSON 内，必须按“排除 `metadata.manifest_sha256` 字段后的 canonical JSON”计算，并提供验证函数。
- 若 `manifest_sha256` 写入旁路 `.sha256` 文件，则必须覆盖最终落盘的 `manifest.json`。
- CSV 不作为完整性校验依据。
```

### MDD-API-006 CleanupAdvisor.list_cleanup_candidates

```text
Input: manifest task_id
Output: CleanupCandidate[]
Preconditions:
- 只能读取 manifest，不得删除任何源端或目标端文件。
Postconditions:
- 仅返回目标端复核通过的 VERIFIED_MATCH 项。
- `VERIFIED_WEAK`、复核失败、目标文件缺失、revision 变化、size/checksum 变化的项目不得进入候选列表。
```

### MDD-API-007 CleanupAdvisor.list_reverification_failures

```text
Input: manifest task_id
Output: ReverificationFailure[]
Preconditions:
- 只能读取 manifest 与目标端 metadata。
Postconditions:
- 返回原本为 VERIFIED_MATCH 但目标端复核失败的项目。
- 每条失败项必须给出原因，例如 target_missing、size_changed、checksum_changed、revision_changed。
- 该列表只用于风险提示，不得作为清理候选。
```

## 4. 安全不变量

- MDD-INV-001：任何模块都不得请求 Apple ID 密码。
- MDD-INV-002：CleanupAdvisor 不持有源端删除接口。
- MDD-INV-003：日志不得包含 OAuth token、refresh token、Apple 账户信息或完整文件内容。
- MDD-INV-004：`VERIFIED_MATCH` 只能由 VerificationEngine 产生。
- MDD-INV-004A：`VERIFIED_WEAK` 不得作为同名文件自动跳过、覆盖或清理候选的依据。
- MDD-INV-005：manifest 不能只记录成功项；失败、跳过、冲突和弱校验都必须记录。
