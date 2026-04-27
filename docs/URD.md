# URD - Idea Brief / 用户需求文档

项目：iCloud 到 Google Drive 迁移工具  
版本：V4 真实接入规划  
文档级别：strict  
日期：2026-04-26

> **项目演进说明**：
> - **Phase 1 (Mock 原型验证)**：已完成。验证了数据结构、状态机和测试用例，全为模拟端点。
> - **Phase 2 (Windows 真实接入)**：进行中。**优先全力实现 Windows 端**，接通真实的本地文件系统与真实的 Google Drive API。
> - **Phase 3 (macOS 真实接入)**：待定。在 Windows 真实端到端跑通之后再实现。

## 1. 项目目标

### URD-GOAL-001 本地迁移

构建一个运行在用户本地设备上的客户端程序，用于把本机已经授权访问的 iCloud 数据迁移到用户授权的 Google Drive。

### URD-GOAL-002 可审计迁移

每条迁移记录都必须有可追溯证据，包括源端标识、目标端标识、路径、大小、哈希、状态和校验时间。

### URD-GOAL-003 手动清理指引

MVP 阶段不执行自动删除，只展示目标端复核通过的“已验证迁移列表”，并引导用户自行在 Finder、资源管理器、Photos 或 iCloud.com 中操作。迁移成功不等于删除源端一定安全，UI 文案不得使用“安全删除”作为默认表达。

## 2. 用户角色

### URD-ROLE-001 普通迁移用户

希望从 iCloud Drive 或 iCloud Photos 迁移数据到 Google Drive，重视数据完整性和避免误删。

### URD-ROLE-002 技术支持/高级用户

需要读取 JSON manifest、失败原因、重试记录和目标 Drive 文件 ID，用于排查迁移问题。

## 3. 产品范围

### 3.1 Phase 2 目标范围（当前真实接入规划）

- URD-REQ-001：本地客户端运行，不通过第三方中转服务器传输文件内容。
- URD-REQ-002：不收集、不保存、不转发 Apple ID、Apple 密码或 2FA 验证码。
- URD-REQ-003：**优先全力完成 Windows 端的真实接入**，macOS 的真实接入延后。
- URD-REQ-004：支持 iCloud Drive 文件迁移。
- URD-REQ-005：支持 iCloud Photos 媒体资产迁移，Windows 只处理已同步到本地的媒体文件。
- URD-REQ-006：支持真实的 Google Drive OAuth 授权，优先使用 `drive.file` 权限。
- URD-REQ-007：上传前后执行真实的本地物理文件哈希与 Google Drive 远端元数据校验。
- URD-REQ-008：输出 JSON 审计清单，并可导出 CSV。
- URD-REQ-009：MVP 不执行自动删除，仅提供手动清理指引。

> 当前代码状态说明：Phase 1 仅完成 Mock 原型验证。以上条目是 Phase 2 真实 Windows 接入的目标范围，不表示当前代码已经能够执行真实 iCloud 到 Google Drive 迁移。

### 3.2 非目标

- URD-NOGOAL-001：不通过网页模拟登录 Apple ID。
- URD-NOGOAL-002：不提供云端直接读取 iCloud 全量数据的服务。
- URD-NOGOAL-003：不保证 Pages、Numbers、Keynote 等文件迁移到 Google Drive 后可在浏览器中直接编辑。
- URD-NOGOAL-004：不对照片或视频进行重编码、压缩或格式转换，除非用户显式选择。
- URD-NOGOAL-005：不调用任何清空“最近删除”或“废纸篓”的接口。
- URD-NOGOAL-006：不把迁移到 Google Drive 等同于迁移到 Google Photos。

## 4. 平台能力矩阵

| 能力 | macOS (Phase 3) | Windows (Phase 2 - 当前优先级) |
|---|---|---|
| iCloud Drive | 暂缓。未来通过系统暴露的 iCloud Drive 文件位置读取；需协调下载中、冲突和失败。 | 真实读取本地目录（如 `~\iCloudDrive`）。通过探测文件流或原生 API 识别未下载的 `.iCloud` 文件，并明确跳过未下载项目。 |
| iCloud Photos | 暂缓。未来使用 PhotoKit 读取。 | 真实扫描本地 iCloud Photos 目录（如 `~\Pictures\iCloud Photos`）。只处理已下载到本地的媒体文件，不恢复相册语义。 |
| Package 文件 | 默认压缩为 `.zip` 后上传，同时记录压缩前文件数、总大小和压缩包哈希 | 视为普通目录或普通文件；需在 UI 中提示可能无法保留 macOS 文档语义 |
| 清理指引 | Finder / Photos / iCloud.com 手动操作 | 资源管理器 / iCloud.com 手动操作 |

## 5. 关键需求

### URD-REQ-010 iCloud Drive 接入

在 Phase 2，工具必须自动或手动配置发现 Windows 本地的 iCloud Drive 物理入口（例如 `%USERPROFILE%\iCloudDrive`）。必须有真实的遍历代码扫描本地文件，只能处理本机已完全下载的文件。遇到 `.iCloud` 等未下载的占位文件时，应提示用户先在资源管理器中“始终保留在此设备上”。

### URD-REQ-011 iCloud Photos 接入

在 Phase 2，Windows 版本只处理 iCloud Photos 默认同步目录（例如 `%USERPROFILE%\Pictures\iCloud Photos`）中已经下载到本地的照片和视频实体文件。由于 Windows 环境没有 PhotoKit，不再承诺关联 Live Photo、RAW+JPEG 或复杂的相册结构。macOS 的 PhotoKit 接入延期至 Phase 3。

### URD-REQ-012 元数据与 sidecar

库级元数据不得强行写回原始媒体文件。标题、相册名、收藏状态、编辑版本说明等信息应写入 `.json` 或 `.xmp` sidecar 文件，并在 manifest 中记录 sidecar 的目标文件 ID。

### URD-REQ-013 Google Drive 授权

默认请求 `drive.file` scope。用户选择已有目标目录时，应通过 Google Picker 或等效机制让用户显式授权该目录。只有在用户启用“扫描整个 Drive 检测重复文件”等高级功能时，才考虑更高权限，并必须单独提示。

### URD-REQ-014 上传协议

5MB 以下文件可使用 multipart upload；大于 5MB 的文件必须使用 resumable upload。resumable upload 的 session URI、已确认字节范围、目标文件 ID 和状态必须持久化。

### URD-REQ-015 强校验

读取源端字节流时必须同时计算 MD5 与 SHA-256。上传完成后，读取 Google Drive 文件元数据，包括 `size`、`md5Checksum`、`sha1Checksum`、`sha256Checksum`、`headRevisionId`。若目标端返回 SHA-256，则优先比对 SHA-256；否则使用 MD5；如果目标对象不能提供字节级 checksum，则只能标记为弱校验，不得标记为 `VERIFIED_MATCH`。

### URD-REQ-016 冲突处理

目标端存在同名文件时，先比对可用 checksum。只有字节级强校验一致时，才能跳过并标记 `SKIPPED_ALREADY_EXISTS`。若仅能得到 `VERIFIED_WEAK`，不得自动跳过，也不得作为“内容一致”的依据，应进入冲突或等待用户确认的状态。内容不同则进入冲突状态，用户可选择跳过、重命名上传、覆盖为新版本。覆盖必须记录旧目标文件 ID、旧 revision 和新 revision。

### URD-REQ-017 审计清单

每次迁移必须生成 JSON manifest。manifest 应具备完整性校验能力：至少包含文件级记录哈希、整体 manifest SHA-256，以及 manifest 生成时间。MVP 的 hash 机制用于检测非预期修改，不承诺抵抗恶意篡改。`manifest_sha256` 必须有明确的计算口径：要么写入独立的 `.sha256` 文件并覆盖最终 JSON 文件，要么在 JSON 内记录时按“排除 `metadata.manifest_sha256` 字段后的 canonical JSON”计算。CSV 只作为人工阅读导出，不作为唯一审计依据。

### URD-REQ-018 任务状态

每条记录必须使用稳定状态码，不允许只写“成功/失败”。最低状态集见 MDD 中的 `MigrationStatus`。

### URD-REQ-019 配额与限流

工具应识别 403、429、5xx 等可重试错误，使用带随机抖动的指数退避。遇到 Google Workspace 上传限制、存储空间不足或用户配额问题时，任务应暂停并提示，不得无提示地长期“静默等待”。

### URD-REQ-020 清理指引

MVP 只展示目标端复核通过的“已验证迁移列表”。展示前应复核目标文件仍存在，并且目标端 `size`、可用 checksum 或 `headRevisionId` 与 manifest 一致。原本为 `VERIFIED_MATCH` 但复核失败的项目不得进入清理候选列表，只能进入风险提示列表并说明原因。工具不得删除 iCloud 文件、照片或最近删除项目。

## 6. 验收标准

### URD-AC-001 凭据安全

整个流程中没有任何代码路径要求用户输入 Apple ID 密码或 2FA 验证码。

### URD-AC-002 本地传输

文件内容只在用户本机读取并上传到 Google Drive，不通过第三方中转服务器。

### URD-AC-003 Drive 文件完整性

所有 `VERIFIED_MATCH` 记录必须能通过源端哈希和目标端可用 checksum 证明内容一致。

### URD-AC-004A Windows Photos 降级验收

Windows Phase 2 仅验收本地已下载媒体文件的迁移完整性、路径映射、哈希校验和 manifest 记录完整性。不验收 Photos Library 的 Live Photo 关联、RAW+JPEG 关联、相册结构、编辑历史或收藏状态。

### URD-AC-004B macOS Photos 资源关联验收

macOS Phase 3 若启用 PhotoKit，则 Live Photo 与 RAW+JPEG 的关联关系必须通过 `resource_group_id` 在 manifest 中查询到。

### URD-AC-005 Manifest 完整性

JSON manifest 必须包含每条迁移记录的源端 ID、源路径、源大小、源哈希、目标 Drive 文件 ID、目标大小、目标 checksum、状态、失败原因、重试次数和校验时间。

### URD-AC-006 断点续传

resumable upload 在程序崩溃后重启，必须能查询服务端已接收字节范围，并从正确位置继续，或明确标记 session 过期并重建上传。

### URD-AC-007 清理安全

MVP 不存在自动删除 iCloud 数据的执行路径。清理页面只能展示手动操作指引和风险提示。

### URD-AC-008 平台差异提示

Windows 版本必须在 UI 中明确说明 Photos 能力限制，不得暗示可完整恢复 macOS Photos Library 语义。

## 7. 约束

### URD-CON-001 隐私约束

工具不得索引、解析、训练或上传用户文件内容到第三方服务。读取文件内容只用于上传、哈希计算和必要的 MIME 判断。

### URD-CON-002 本地日志约束

任务状态、OAuth token、manifest 草稿和哈希记录只保存在用户本机。token 必须进入系统安全存储，不得以明文写入普通日志。

### URD-CON-003 API 约束

不得依赖未公开、不可测试或容易被风控阻断的 iCloud 网页接口。Apple 和 Google API 行为变更时，相关功能必须降级为不可用并提示用户。

## 8. 假设

### URD-ASM-001

用户已经在本机登录 iCloud，并启用了 iCloud Drive 或 iCloud Photos。

### URD-ASM-002

Google Drive OAuth 应用已经通过必要的发布和验证流程，至少能在测试用户范围内使用。

### URD-ASM-003

MVP 不实现 Google Photos 迁移，也不实现跨设备自动清理。

## 9. 未决问题

### URD-Q-001

macOS 上触发 iCloud Drive 占位文件下载的具体接口路径需要原型验证，并应覆盖不同 macOS 版本。

### URD-Q-002

Windows 上 iCloud Photos 的目录结构、下载状态标识和文件可用性需要在 iCloud for Windows 当前版本上验证。

### URD-Q-003

是否需要为 manifest 做本地签名，还是使用 hash chain 与整体 SHA-256 即可满足 MVP 审计需求？
