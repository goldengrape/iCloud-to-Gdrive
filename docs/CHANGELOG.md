# CHANGELOG

## 2026-04-26

- 首批 RMD 任务（RMD-TASK-001 至 RMD-TASK-012）代码已全面实现，并完成所有本地与集成测试（测试通过率 100%）。
- 使用 Vibe Coding Skill strict 文档结构整理 V3 URD。
- 新增 `docs/URD.md`、`docs/ADD.md`、`docs/MDD.md`、`docs/TDD.md`、`docs/RMD.md`、`docs/TRACE.md`。
- 新增 wiki 短笔记，按需求、决策、模块、接口、测试和实现路径拆分。
- 明确 MVP 不自动删除 iCloud 数据。
- 明确 Windows Photos 能力降级，不承诺完整恢复 Photos Library 语义。
- 将“不可篡改 JSON 审计清单”细化为 record_hash + manifest_sha256；本地签名作为未决问题保留。
