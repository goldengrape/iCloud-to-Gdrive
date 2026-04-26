# Manifest

来源：URD-REQ-017、MDD-DATA-004、MDD-API-005。

## 定义

Manifest 是每次迁移任务的审计清单。JSON 是权威格式，CSV 只用于人工阅读。

## 为什么重要

后续清理指引只能依据 manifest 中的 `VERIFIED_MATCH` 记录，并且展示前还要重新检查目标文件仍存在。

## 防篡改

MVP 至少需要：

- 每条记录的 `record_hash`
- 整体 `manifest_sha256`
- 生成时间

签名机制放在后续版本。
