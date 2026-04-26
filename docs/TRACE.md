# TRACE - Project Map / 追踪表

## 1. 需求到设计追踪

| URD | ADD | MDD | TDD | RMD | Wiki |
|---|---|---|---|---|---|
| URD-REQ-001 | ADD-FR-001 | MDD-MOD-002 | TDD-TEST-002 | RMD-TASK-008, RMD-TASK-010 | wiki/decisions/DEC-001-local-client.md |
| URD-REQ-002 | ADD-FR-009 | MDD-MOD-011 | TDD-TEST-001, TDD-TEST-020 | RMD-TASK-006 | wiki/requirements/security-boundaries.md |
| URD-REQ-003 | ADD-FR-001, ADD-FR-002 | MDD-MOD-001 | TDD-TEST-004, TDD-TEST-008 | RMD-TASK-008, RMD-TASK-009, RMD-TASK-010 | wiki/requirements/platform-matrix.md |
| URD-REQ-010 | ADD-FR-001 | MDD-MOD-002 | TDD-TEST-003, TDD-TEST-004 | RMD-TASK-008, RMD-TASK-010 | wiki/modules/source-adapters.md |
| URD-REQ-011 | ADD-FR-002, ADD-FR-003 | MDD-MOD-003, MDD-MOD-004 | TDD-TEST-005, TDD-TEST-006 | RMD-TASK-009, RMD-TASK-010 | wiki/modules/source-adapters.md |
| URD-REQ-012 | ADD-FR-003 | MDD-MOD-004 | TDD-TEST-007 | RMD-TASK-009 | wiki/terms/manifest.md |
| URD-REQ-013 | ADD-FR-004, ADD-FR-009 | MDD-MOD-005, MDD-MOD-011 | TDD-TEST-008 | RMD-TASK-006 | wiki/requirements/security-boundaries.md |
| URD-REQ-014 | ADD-FR-004, ADD-FR-006 | MDD-MOD-005, MDD-DATA-003 | TDD-TEST-009 | RMD-TASK-007 | wiki/modules/upload-verifier.md |
| URD-REQ-015 | ADD-FR-005 | MDD-MOD-006 | TDD-TEST-010, TDD-TEST-011, TDD-TEST-012 | RMD-TASK-004 | wiki/modules/upload-verifier.md |
| URD-REQ-016 | ADD-FR-003, ADD-FR-004 | MDD-MOD-004, MDD-MOD-005 | TDD-TEST-013, TDD-TEST-014 | RMD-TASK-011 | wiki/modules/upload-verifier.md |
| URD-REQ-017 | ADD-FR-007 | MDD-MOD-009, MDD-DATA-004 | TDD-TEST-015 | RMD-TASK-003 | wiki/interfaces/manifest-record.md |
| URD-REQ-018 | ADD-FR-006 | MDD-DATA-005 | TDD-TEST-015 | RMD-TASK-002 | wiki/interfaces/manifest-record.md |
| URD-REQ-019 | ADD-FR-006 | MDD-MOD-008 | TDD-TEST-016, TDD-TEST-017 | RMD-TASK-007 | wiki/modules/upload-verifier.md |
| URD-REQ-020 | ADD-FR-008 | MDD-MOD-010 | TDD-TEST-018, TDD-TEST-019 | RMD-TASK-012 | wiki/decisions/DEC-002-mvp-no-delete.md |

## 2. 决策追踪

| Decision | 来源 | 影响 |
|---|---|---|
| DEC-001 本地客户端 | URD-REQ-001, URD-REQ-002 | 禁止云端中转和 Apple ID 密码输入 |
| DEC-002 MVP 不自动删除 | URD-REQ-020, URD-AC-007 | CleanupAdvisor 只读，不持有删除接口 |
| DEC-003 Windows Photos 降级 | URD-REQ-003, URD-REQ-011 | Windows 只承诺目录文件迁移 |

## 3. 未决问题追踪

| 问题 | 来源 | 当前处理 |
|---|---|---|
| PROB-001 macOS 占位文件下载接口验证 | URD-Q-001 | 原型阶段验证，发布前必须关闭 |
| PROB-002 Windows iCloud Photos 下载状态 | URD-Q-002 | 原型阶段验证，无法验证则降级为手动本地目录模式 |
| PROB-003 manifest 防篡改级别 | URD-Q-003 | MVP 采用 record_hash + manifest_sha256，签名放入停车场 |
