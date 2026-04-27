# 平台能力矩阵

来源：URD-REQ-003、URD-REQ-010、URD-REQ-011、URD-AC-008。

## 核心结论

macOS 和 Windows 不能按同等能力实现。

## macOS（Phase 3）

- iCloud Drive：本地 iCloud Drive 文件，读取时要处理同步、占位、下载中和 package。
- Photos：PhotoKit 模式，支持 Photos Library 中的资产关系。
- Package：默认压缩成 `.zip` 上传，保留压缩前文件数和大小。
- 这些能力不是当前 Phase 2 Windows MVP 的实现范围。

## Windows（Phase 2 当前优先）

- iCloud Drive：iCloud for Windows 暴露的本地目录。
- Photos：只处理本地同步目录中的媒体文件。
- 不承诺恢复 Live Photo、RAW+JPEG、相册结构和编辑历史。

## 测试入口

- TDD-TEST-003
- TDD-TEST-004
- TDD-TEST-008
