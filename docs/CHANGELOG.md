# CHANGELOG

## 2026-04-27

### 任务更新

- 完成了 RMD-TASK-016：实现 CLI 入口与端到端串联，集成了 `RealWindowsICloudAdapter`、`RealGoogleDriveAdapter`、`VerificationEngine` 和 `TaskStore`。
- 新增 `src/rmd/engine.py` 实现文件迁移调度器。
- 新增 `src/rmd/main.py` 作为 `argparse` 的统一命令行入口。
- 新增文件级别的断点续传能力（对 `VERIFIED_MATCH` 状态的文件予以跳过）。
- 完成了 RMD-TASK-017：Windows 真实环境集成测试，成功运行所有相关 `pytest` 和 E2E 脚本。

## 2026-04-26

- 将 URD 的“当前版本范围”改为 Phase 2 目标范围，明确当前代码仍处于 Mock 原型验证后状态。
- 将 Windows Photos 验收与 macOS PhotoKit 验收拆分，避免 Windows MVP 被 Live Photo / RAW+JPEG 关系验收阻塞。
- 将 manifest 从“防篡改”改为“完整性校验”，明确 `manifest_sha256` 的计算口径。
- 明确 `VERIFIED_WEAK` 不得作为同名文件自动跳过、覆盖或清理候选依据。
- 将 CleanupAdvisor 拆成清理候选列表与复核失败风险列表两类输出。
- 同步更新 TDD、TRACE 与 wiki。
- 新增 RMD-TASK-012A，作为进入真实 Windows 接入前的 Mock 契约修复任务。

- 首批 RMD 任务（RMD-TASK-001 至 RMD-TASK-012）代码已全面实现，并完成所有本地与集成测试（测试通过率 100%）。
- 使用 Vibe Coding Skill strict 文档结构整理 V3 URD。
- 新增 `docs/URD.md`、`docs/ADD.md`、`docs/MDD.md`、`docs/TDD.md`、`docs/RMD.md`、`docs/TRACE.md`。
- 新增 wiki 短笔记，按需求、决策、模块、接口、测试和实现路径拆分。
- 明确 MVP 不自动删除 iCloud 数据。
- 明确 Windows Photos 能力降级，不承诺完整恢复 Photos Library 语义。
- 将“不可篡改 JSON 审计清单”细化为 record_hash + manifest_sha256；本地签名作为未决问题保留。
