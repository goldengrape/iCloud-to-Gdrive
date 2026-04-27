# TDD - Check Plan / 测试计划文档

测试目标：证明迁移工具不会乱拿凭据、不会漏记录、不会把弱校验当强校验，也不会在 MVP 中执行自动删除。

## 1. 测试策略

> **当前阶段声明 (Phase 1)**：原有 Mock 测试已通过，但它们全数运行在基于内存字典的 Mock 适配器上，只证明了核心逻辑和状态机的雏形。文档修复后新增或细化的测试项（例如 `TDD-TEST-006W`、`TDD-TEST-016A/B`、manifest hash 可验证性、弱校验不自动跳过）需要补充实现，不能视为当前代码已通过。

- 单元测试：数据结构、状态机、哈希比对、错误分类（已通过 Mock 验证）。
- 合同测试：SourceAdapter、GoogleDriveTargetAdapter、ManifestWriter、CleanupAdvisor。
- 集成测试：本地假源端到假 Drive 目标端（已通过）。
- **(Phase 2 新增) 端到端真实环境测试 (E2E)**：在真实的 Windows 文件系统和真实的 Google Drive API 环境下运行完整数据流转。
- 平台测试：Windows iCloud for Windows（当前优先）、macOS iCloud Drive（延期）、macOS Photos（延期）。
- 负向测试：权限拒绝、占位文件、配额、限流、文件变化、session 过期、目标文件被删除。

## 2. 测试用例

| Test ID | 验证目标 | 关联需求 | 判定依据 |
|---|---|---|---|
| TDD-TEST-001 | 不收集 Apple ID 密码 | URD-REQ-002, URD-AC-001 | UI、配置、日志、接口中不存在 Apple ID 密码输入或字段 |
| TDD-TEST-002 | 本地传输路径 | URD-REQ-001, URD-AC-002 | 网络请求只发往 Google OAuth/Drive API，不向第三方上传文件内容 |
| TDD-TEST-003 | macOS iCloud Drive 占位文件状态 | URD-REQ-010 | 未下载文件进入 SOURCE_PLACEHOLDER 或 SOURCE_DOWNLOADING，完成后才上传 |
| TDD-TEST-004 | Windows 未下载文件处理 | URD-REQ-010, URD-AC-008 | 未下载文件不会被当作成功项，UI 提示用户先下载到本机 |
| TDD-TEST-005 | macOS Live Photo 关联（Phase 3） | URD-REQ-011, URD-AC-004B | 静态图与 MOV 两条记录拥有相同 resource_group_id；不作为 Windows Phase 2 必验项 |
| TDD-TEST-006 | macOS RAW+JPEG 关联（Phase 3） | URD-REQ-011, URD-AC-004B | RAW 与 JPEG 两条记录拥有相同 resource_group_id 且 resource_kind 不同；不作为 Windows Phase 2 必验项 |
| TDD-TEST-006W | Windows Photos 降级验收 | URD-REQ-011, URD-AC-004A, URD-AC-008 | 只验收本地已下载媒体文件的迁移完整性，不要求相册、Live Photo 或 RAW+JPEG 资产关系 |
| TDD-TEST-007 | Sidecar 生成 | URD-REQ-012 | 库级元数据写入 sidecar，原始媒体文件未被修改 |
| TDD-TEST-008 | drive.file 权限 | URD-REQ-013 | OAuth 请求默认只包含 drive.file 与必要最小辅助 scope |
| TDD-TEST-009 | resumable upload session 持久化 | URD-REQ-014, URD-AC-006 | 进程重启后能读取 session URI 并查询 Range 继续上传 |
| TDD-TEST-010 | SHA-256 优先校验 | URD-REQ-015, URD-AC-003 | 目标返回 sha256Checksum 时以 SHA-256 为最终判定 |
| TDD-TEST-011 | MD5 降级校验 | URD-REQ-015 | 目标仅返回 md5Checksum 时，使用本地 MD5 比对并保留 SHA-256 证据 |
| TDD-TEST-012 | checksum 不可用弱校验 | URD-REQ-015 | checksum 不可用时状态为 VERIFIED_WEAK，不得为 VERIFIED_MATCH |
| TDD-TEST-013 | 目标同名强校验一致跳过 | URD-REQ-016 | 字节级强校验一致时状态为 SKIPPED_ALREADY_EXISTS，不重复上传 |
| TDD-TEST-014 | 目标同名冲突 | URD-REQ-016 | 哈希不同进入 CONFLICT_TARGET_EXISTS，不自动覆盖；VERIFIED_WEAK 不得自动跳过 |
| TDD-TEST-015 | manifest 字段完整与完整性校验 | URD-REQ-017, URD-AC-005 | 每条记录含必填字段、record_hash；manifest_sha256 能按声明口径验证最终 JSON 或 canonical JSON |
| TDD-TEST-016A | Drive 错误分类（Mock） | URD-REQ-019 | 429/403/5xx、quota、storage 错误能映射到正确状态 |
| TDD-TEST-016B | 限流退避调度 | URD-REQ-019 | 429/403 rate limit 触发带随机抖动的指数退避，并记录下一次重试时间 |
| TDD-TEST-017 | 配额暂停 | URD-REQ-019 | storage quota 或 750GB 类错误进入 UPLOAD_PAUSED_QUOTA 并提示用户 |
| TDD-TEST-018 | 清理候选目标复核 | URD-REQ-020 | 展示前重新读取目标 size/checksum/revision；只展示复核通过项，复核失败项进入风险提示列表 |
| TDD-TEST-019 | 禁止自动删除 | URD-REQ-020, URD-AC-007 | MVP 构建中不存在 iCloud 删除接口调用路径 |
| TDD-TEST-020 | 日志脱敏 | URD-CON-002 | 日志中不出现 token、完整文件内容、Apple 账户凭据 |

### 2.1 端到端与真实环境测试 (Phase 2 新增)

| Test ID | 验证目标 | 关联需求 | 判定依据 |
|---|---|---|---|
| E2E-TEST-001 | Windows 真实文件扫描 | URD-REQ-010 | 在测试目录中放置真实文件与 `.iCloud` 快捷方式，工具能准确跳过 `.iCloud` 文件 |
| E2E-TEST-002 | 真实 Google OAuth 授权 | URD-REQ-013 | 能够成功拉开浏览器授权并获取有效的 `drive.file` scope token，存储到 Windows Credential Manager |
| E2E-TEST-003 | 真实 Google Drive API 上传 | URD-REQ-014 | 5MB 以下文件成功直传，大于 5MB 文件触发 Resumable Upload 成功，Drive 中出现实体文件 |
| E2E-TEST-004 | 真实的 SHA-256 远端校验 | URD-REQ-015 | 根据 E2E-TEST-003 结果，比对 Drive API 返回的元数据 `sha256Checksum` 与本地计算哈希一致 |
| E2E-TEST-005 | CLI 流程闭环 | ADD-FR-010 | 用户通过终端执行 `python main.py`，经历完整的【授权->扫描->上传->校验->生成 manifest】闭环 |

## 3. 关键测试数据

### TDD-DATA-001 小文件

- 0 字节文件
- 1KB 文本文件
- 4.9MB 二进制文件

### TDD-DATA-002 大文件

- 5.1MB 文件，验证 resumable upload
- 2GB 文件，验证 offset 与内存占用
- 模拟 10GB 文件，验证任务状态和分片逻辑，可用 sparse file 或 mock stream

### TDD-DATA-003 复合资源

- `.pages` package
- macOS Phase 3 Live Photo：HEIC/JPG + MOV
- macOS Phase 3 RAW+JPEG
- Windows Phase 2 普通照片/视频文件
- 带 sidecar 的照片资产

### TDD-DATA-004 失败输入

- 权限拒绝目录
- 下载中的占位文件
- 源文件在上传中被删除
- 目标 Drive 文件在清理复核前被删除
- 目标 Drive 返回 429、403、5xx

## 4. 停止条件

- TDD-STOP-001：若无法稳定检测某平台的源文件下载状态，停止该平台迁移功能，只保留手动选择本地已下载文件模式。
- TDD-STOP-002：若 Google Drive 目标端无法返回任何强校验字段，不能把结果标记为 `VERIFIED_MATCH`。
- TDD-STOP-003：若发现任何自动删除路径进入 MVP 构建，发布流程必须停止。
- TDD-STOP-004：若 manifest 不能记录失败项或冲突项，发布流程必须停止。
