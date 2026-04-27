# Manifest

来源：URD-REQ-017、MDD-DATA-004、MDD-API-005。

## 定义

Manifest 是每次迁移任务的审计清单。JSON 是权威格式，CSV 只用于人工阅读。

## 为什么重要

后续清理指引只能依据 manifest 中的 `VERIFIED_MATCH` 记录，并且展示前还要重新检查目标文件仍存在。

## 完整性校验

MVP 至少需要：

- 每条记录的 `record_hash`
- 整体 `manifest_sha256`
- 生成时间

这只能检测非预期修改，不承诺抵抗恶意篡改。签名机制放在后续版本。

`manifest_sha256` 需要明确计算口径：写在 JSON 内时排除自身字段并使用 canonical JSON；写在旁路 `.sha256` 文件时覆盖最终 JSON 文件。
