# RMD - Build Path / 开发路线文档

开发原则：先固定数据结构和测试判定，再接入真实平台。每个任务完成后更新文档与 wiki，并建立 Git 检查点。

## 1. 实现顺序

### RMD-TASK-001 初始化项目骨架 [已完成]

目标：建立客户端项目目录、测试目录、文档目录、CI 基础检查。  
依赖：无。  
测试命令：`pytest` 或平台对应单元测试命令。  
Git 检查点：`feat/rmd-task-001-project-skeleton`。

### RMD-TASK-002 定义核心数据结构和状态机 [已完成]

目标：实现 `TransferItem`、`ManifestRecord`、`MigrationStatus`、`DriveUploadSession`。  
依赖：RMD-TASK-001。  
测试：TDD-TEST-015。  
Git 检查点：`feat/rmd-task-002-core-models`。

### RMD-TASK-003 实现 TaskStore 与 ManifestWriter [已完成]

目标：SQLite 状态持久化、JSON manifest、CSV 导出、record_hash、manifest_sha256。  
依赖：RMD-TASK-002。  
测试：TDD-TEST-015、TDD-TEST-020。  
Git 检查点：`feat/rmd-task-003-taskstore-manifest`。

### RMD-TASK-004 实现 VerificationEngine [已完成]

目标：流式计算 MD5/SHA-256，执行 SHA-256 优先、MD5 降级、弱校验规则。  
依赖：RMD-TASK-002。  
测试：TDD-TEST-010、TDD-TEST-011、TDD-TEST-012。  
Git 检查点：`feat/rmd-task-004-verification-engine`。

### RMD-TASK-005 实现假源端与假目标端集成测试 [已完成]

目标：不依赖真实 iCloud 或 Google Drive，先跑通 list → stream → hash → upload → verify → manifest。  
依赖：RMD-TASK-003、RMD-TASK-004。  
测试：TDD-TEST-002、TDD-TEST-015。  
Git 检查点：`feat/rmd-task-005-fake-adapters`。

### RMD-TASK-006 实现 Google Drive OAuth 与目标目录授权 [已完成]

目标：默认 `drive.file`，支持用户选择目标目录，token 进入系统安全存储。  
依赖：RMD-TASK-005。  
测试：TDD-TEST-008、TDD-TEST-020。  
Git 检查点：`feat/rmd-task-006-google-auth`。

### RMD-TASK-007 实现 Google Drive multipart / resumable upload [已完成]

目标：5MB 阈值、session URI 持久化、Range 查询、offset 续传、错误分类。  
依赖：RMD-TASK-006。  
测试：TDD-TEST-009、TDD-TEST-016、TDD-TEST-017。  
Git 检查点：`feat/rmd-task-007-drive-upload`。

### RMD-TASK-008 实现 macOS iCloud Drive 适配器 [已完成]

目标：读取本地 iCloud Drive，处理 package、占位、下载中、权限失败。  
依赖：RMD-TASK-005。  
测试：TDD-TEST-003、TDD-TEST-014。  
Git 检查点：`feat/rmd-task-008-macos-icloud-drive`。

### RMD-TASK-009 实现 macOS Photos 适配器 [已完成]

目标：PhotoKit 读取原始资源、Live Photo、RAW+JPEG、相册元数据和 sidecar。  
依赖：RMD-TASK-005。  
测试：TDD-TEST-005、TDD-TEST-006、TDD-TEST-007。  
Git 检查点：`feat/rmd-task-009-macos-photos`。

### RMD-TASK-010 实现 Windows iCloud 文件目录适配器 [已完成]

目标：读取 iCloud for Windows Drive/Photos 目录，识别未下载或不可读文件，输出平台限制提示。  
依赖：RMD-TASK-005。  
测试：TDD-TEST-004、TDD-TEST-008。  
Git 检查点：`feat/rmd-task-010-windows-icloud-files`。

### RMD-TASK-011 实现冲突处理和用户选择 [已完成]

目标：同名同哈希跳过，同名不同哈希进入冲突，用户选择重命名、跳过或覆盖。  
依赖：RMD-TASK-007。  
测试：TDD-TEST-013、TDD-TEST-014。  
Git 检查点：`feat/rmd-task-011-conflict-policy`。

### RMD-TASK-012 实现清理指引 [已完成]

目标：只读读取 manifest，复核目标端仍存在，展示手动清理指引和风险提示。  
依赖：RMD-TASK-003、RMD-TASK-007。  
测试：TDD-TEST-018、TDD-TEST-019。  
Git 检查点：`feat/rmd-task-012-cleanup-advisor`。

## 2. 发布前检查

- RMD-STOP-001：所有 `VERIFIED_MATCH` 必须有强校验依据。
- RMD-STOP-002：任何自动删除代码路径出现时停止发布。
- RMD-STOP-003：Windows Photos 文案必须明确能力限制。
- RMD-STOP-004：manifest 必须能重建每条记录从源端到目标端的迁移证据。

## 3. 回滚点

- RMD-ROLLBACK-001：数据结构和状态机完成后打 tag。
- RMD-ROLLBACK-002：假源端到假目标端闭环完成后打 tag。
- RMD-ROLLBACK-003：Google Drive 上传与校验完成后打 tag。
- RMD-ROLLBACK-004：每个平台适配器单独完成后打 tag。

## 4. 文档维护规则

- 修改需求先更新 URD。
- 修改模块边界更新 ADD / MDD。
- 修改验收方式更新 TDD。
- 修改实现顺序更新 RMD。
- 每次文档变化更新 TRACE 和 wiki。
