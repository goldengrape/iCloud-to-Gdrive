# 开发日志 (Development Log)

## 2026-04-26
- **里程碑**: 首批 RMD 任务 Mock 验证完成 (RMD-TASK-001 至 RMD-TASK-012)
- **状态**: 核心 Mock 模块已实现并经过测试验证 (`pytest` 结果全绿，共 29 个测试用例全部通过)。
- **已完成任务列表**:
  - RMD-TASK-001: 初始化项目骨架
  - RMD-TASK-002: 定义核心数据结构和状态机
  - RMD-TASK-003: 实现 TaskStore 与 ManifestWriter
  - RMD-TASK-004: 实现 VerificationEngine
  - RMD-TASK-005: 实现假源端与假目标端集成测试
  - RMD-TASK-006: 实现 Google Drive OAuth 与目标目录授权
  - RMD-TASK-007: 实现 Google Drive multipart / resumable upload
  - RMD-TASK-008: 实现 macOS iCloud Drive 适配器
  - RMD-TASK-009: 实现 macOS Photos 适配器
  - RMD-TASK-010: 实现 Windows iCloud 文件目录适配器
  - RMD-TASK-011: 实现冲突处理和用户选择
  - RMD-TASK-012: 实现清理指引
- **备注**: Mock 主体流程打通，路线图 RMD.md 已同步更新标注 RMD-TASK-001 至 RMD-TASK-012 为“[已完成 (Mock验证阶段)]”。当前尚不可作为真实迁移工具运行。
- **追加**: 完成 RMD-TASK-012A 修复 Mock 阶段文档契约缺口，正式进入 Phase 2 Windows 真实接入阶段。
- **2026-04-26**: 完成 RMD-TASK-013，接入 `google-auth-oauthlib` 和 `keyring`，实现了真实的 Google OAuth 端到端凭据获取和安全存储，完成 Phase 2 的第一步。
- **2026-04-26**: 完成 RMD-TASK-014，引入 `google-api-python-client`，通过 `RealGoogleDriveAdapter` 实现了 `MediaIoBaseUpload` 的真实 Google Drive 文件分块上传与续传，并能自动创建和定位 `iCloud-to-Gdrive-Migration` 专用目录。
- **2026-04-27**: 完成 RMD-TASK-015，实现 `RealWindowsICloudAdapter`，真实遍历 Windows 本地 iCloud 目录，并通过位掩码比对精准识别 `FILE_ATTRIBUTE_OFFLINE` 以及 `.iCloud` 扩展名的空壳占位符文件。
