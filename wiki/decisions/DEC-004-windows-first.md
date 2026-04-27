# DEC-004-windows-first

## 上下文
在 Phase 1 阶段，我们成功构建了核心数据结构、验证引擎、任务流转状态机以及所有的假端点（Mock Adapters），并跑通了 29 个核心单元测试。然而，目前的系统还无法真正运行以迁移文件。

为了尽快获得一个可用且产生实际价值的产品，我们面临平台优先级的选择：是先做 macOS 的真实物理接入，还是先做 Windows 的真实物理接入。

## 决策
**优先全力实现 Windows 端的真实物理接入（Phase 2），暂缓 macOS 的真实物理接入（推迟至 Phase 3）。**

## 理由
1. **当前开发环境限制**：开发者目前主要在 Windows 环境下进行构建与调试，实现 Windows 的物理文件遍历和 Google Drive OAuth 接入的反馈循环最短。
2. **风险分离**：macOS 上的 `PhotoKit` 接入以及 iCloud Drive 下载协调涉及到极其复杂的操作系统级别 API (如 `NSFileCoordinator` 或 `PyObjC`)。优先在 Windows 上实现基于标准文件目录结构（`~\iCloudDrive`, `~\Pictures\iCloud Photos`）的端到端串联，可以将“Google Drive 真实上传逻辑”与“复杂操作系统的适配逻辑”分步解决，降低项目风险。
3. **尽早提供产品价值**：只要跑通了基于 Windows 目录的扫描、防占位符、断点续传与哈希比对，工具就已经具备了跨网盘搬运大量实实在在照片和文档的能力，达到 MVP 实用标准。

## 影响
- 在 `URD.md` 的平台能力矩阵中明确了 Windows 处于 Phase 2 优先级，macOS 处于 Phase 3 优先级。
- `RMD.md` 中的接下来的任务路线图 (RMD-TASK-013 到 RMD-TASK-017) 全部围绕 Windows E2E 开展。
- `TDD.md` 新增的 E2E 测试主要针对 Windows 本地目录结构。
