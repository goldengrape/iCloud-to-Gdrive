# Build Path 摘要

来源：RMD.md。

## Phase 1：Mock 验证阶段（已完成）

RMD-TASK-001 至 RMD-TASK-012 已完成，但这些实现运行在 Mock / Dummy 适配器上，只证明核心数据结构、状态机、校验规则和 manifest 输出的雏形。它们不能被描述为真实迁移能力完成。

## Phase 1.5：契约修复（未完成）

- RMD-TASK-012A：修复稳定 record_id、manifest hash 可验证、弱校验不自动跳过、清理候选只含复核通过项等文档契约缺口。

## Phase 2：Windows 真实接入（进行中，当前优先）

- RMD-TASK-013：真实 Google OAuth 与系统安全存储。
- RMD-TASK-014：真实 Google Drive 分块上传与续传。
- RMD-TASK-015：真实 Windows iCloud Drive / Photos 本地扫描。
- RMD-TASK-016：CLI 入口与端到端串联。
- RMD-TASK-017：Windows 真实环境集成测试。

## Phase 3：macOS 真实接入（待定）

macOS iCloud Drive 文件协调、PhotoKit、Live Photo / RAW+JPEG 资产关系和 package 高保真处理放在 Phase 3。

## 停止条件

- 强校验不能成立。
- 出现自动删除路径。
- manifest 不能记录失败或冲突。
- 平台下载状态无法可靠识别且没有降级方案。
