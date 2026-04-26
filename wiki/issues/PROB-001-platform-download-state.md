# PROB-001 平台下载状态验证

来源：URD-Q-001、URD-Q-002、TDD-STOP-001。

## 问题

不同 macOS / Windows 版本对 iCloud 占位文件、下载状态、保留到本机的表现可能不同。V3 URD 中的具体接口路径仍需原型验证。

## 当前处理

- macOS：原型验证 iCloud Drive 占位文件如何触发下载、如何观察进度、如何处理失败。
- Windows：原型验证 iCloud for Windows 的文件状态标记和 Photos 目录结构。

## 发布要求

如果某平台不能稳定检测下载状态，该平台只能提供“用户手动选择本地已下载目录”的降级模式。
