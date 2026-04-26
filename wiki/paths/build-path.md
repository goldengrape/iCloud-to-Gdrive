# Build Path 摘要

来源：RMD.md。

## 顺序

1. 项目骨架。
2. 核心数据结构和状态机。
3. TaskStore 与 ManifestWriter。
4. VerificationEngine。
5. 假源端与假目标端。
6. Google OAuth。
7. Google Drive 上传与续传。
8. macOS iCloud Drive。
9. macOS Photos。
10. Windows iCloud 文件目录。
11. 冲突处理。
12. 清理指引。

## 停止条件

- 强校验不能成立。
- 出现自动删除路径。
- manifest 不能记录失败或冲突。
- 平台下载状态无法可靠识别且没有降级方案。
