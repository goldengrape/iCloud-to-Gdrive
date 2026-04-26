# ADD - Design Split / 设计拆分文档

本文把 URD 中的需求拆成可独立实现和测试的功能需求（FR）与设计参数（DP）。目标不是追求漂亮矩阵，而是让实现顺序清楚、模块边界稳定。

## 1. 功能需求与设计参数

| FR ID | 功能需求 | 关联 URD | DP ID | 设计参数 |
|---|---|---|---|---|
| ADD-FR-001 | 本地安全接入 iCloud Drive | URD-REQ-001, URD-REQ-010 | ADD-DP-001 | PlatformSourceAdapter：按平台实现 Drive 文件读取 |
| ADD-FR-002 | 本地安全接入 iCloud Photos | URD-REQ-003, URD-REQ-011 | ADD-DP-002 | PhotoSourceAdapter：macOS PhotoKit + Windows 文件目录模式 |
| ADD-FR-003 | 处理复合资源和 package | URD-REQ-011, URD-REQ-012, URD-REQ-016 | ADD-DP-003 | ResourceNormalizer：输出统一 ResourceGroup 与 TransferItem |
| ADD-FR-004 | 授权并写入 Google Drive | URD-REQ-006, URD-REQ-013, URD-REQ-014 | ADD-DP-004 | GoogleDriveTargetAdapter：OAuth、目录选择、上传会话 |
| ADD-FR-005 | 执行哈希与目标校验 | URD-REQ-015 | ADD-DP-005 | VerificationEngine：MD5/SHA-256 流式计算与 Drive 元数据比对 |
| ADD-FR-006 | 管理任务、续传和重试 | URD-REQ-014, URD-REQ-018, URD-REQ-019 | ADD-DP-006 | TaskStore + RetryScheduler：SQLite 状态、offset、限流退避 |
| ADD-FR-007 | 生成审计 manifest | URD-REQ-017, URD-AC-005 | ADD-DP-007 | ManifestWriter：JSON、CSV、记录哈希、整体 SHA-256 |
| ADD-FR-008 | 展示手动清理指引 | URD-REQ-020, URD-AC-007 | ADD-DP-008 | CleanupAdvisor：只读复核、可删除清单、风险提示 |
| ADD-FR-009 | 保护凭据和本地隐私 | URD-REQ-002, URD-CON-001, URD-CON-002 | ADD-DP-009 | SecurityBoundary：系统钥匙串/凭据管理、日志脱敏 |

## 2. 设计矩阵

`X` 表示该设计参数直接满足该功能需求，`△` 表示有轻微依赖。

| FR \ DP | DP-001 | DP-002 | DP-003 | DP-004 | DP-005 | DP-006 | DP-007 | DP-008 | DP-009 |
|---|---|---|---|---|---|---|---|---|---|
| FR-001 iCloud Drive 接入 | X |  | △ |  |  | △ |  |  | △ |
| FR-002 iCloud Photos 接入 |  | X | △ |  |  | △ |  |  | △ |
| FR-003 复合资源处理 | △ | △ | X |  | △ |  | △ |  |  |
| FR-004 Google Drive 写入 |  |  |  | X | △ | △ |  |  | △ |
| FR-005 校验 |  |  | △ | △ | X | △ | △ |  |  |
| FR-006 续传重试 | △ | △ |  | △ |  | X | △ |  |  |
| FR-007 manifest |  |  | △ | △ | △ | △ | X | △ |  |
| FR-008 清理指引 | △ | △ |  | △ | △ |  | △ | X | △ |
| FR-009 安全边界 | △ | △ |  | △ |  | △ | △ | △ | X |

## 3. 耦合分析

### ADD-COUP-001 源端读取与任务状态耦合

源端读取会影响状态机，例如占位文件、下载中、源文件消失。此耦合合理，因为状态机必须准确反映源端可读性。

防护：SourceAdapter 只能输出标准化状态事件，不能直接写 UI 或 Drive 上传逻辑。

### ADD-COUP-002 Google Drive 上传与校验耦合

Drive 上传后必须读取目标 metadata 才能校验。此耦合合理。

防护：TargetAdapter 负责上传和读取元数据，VerificationEngine 负责判定，不把校验规则写在上传模块里。

### ADD-COUP-003 Manifest 与多个模块耦合

Manifest 需要源端、目标端、校验和任务状态数据。这是审计类功能的必然耦合。

防护：使用统一 `ManifestRecord` 数据结构。所有模块只追加字段或事件，不直接拼接最终 JSON。

## 4. 执行顺序

1. 定义数据结构和状态机。
2. 实现 TaskStore 与 ManifestWriter 的最小版本。
3. 实现本地假源端和假 Drive 目标端，先跑通校验链。
4. 实现 Google Drive OAuth 和 resumable upload。
5. 实现 macOS iCloud Drive 适配器。
6. 实现 macOS Photos 适配器。
7. 实现 Windows 文件目录适配器。
8. 实现清理指引页面。

## 5. 接受的设计取舍

### DEC-001 MVP 只做本地客户端

避免 Apple ID 密码、2FA、网页模拟登录和第三方中转服务器风险。

### DEC-002 MVP 不自动删除

迁移成功不等于删除一定安全。MVP 只展示已验证迁移列表和手动操作指引。

### DEC-003 Photos Windows 版本降级

Windows 没有 PhotoKit。MVP 将 Windows Photos 视为已同步到本地的媒体文件集合。
