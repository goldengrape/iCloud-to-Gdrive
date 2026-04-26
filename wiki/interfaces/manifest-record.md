# ManifestRecord

来源：URD-REQ-017、URD-AC-005、MDD-DATA-004、MDD-API-005。

## 用途

ManifestRecord 是清理建议和排查问题的依据。它必须记录成功、失败、跳过、冲突和弱校验。

## 必填信息

- 任务和记录 ID：`task_id`、`record_id`
- 源端证据：`source_stable_id`、`source_path`、`source_size`、`source_md5`、`source_sha256`
- 目标证据：`target_drive_file_id`、`target_size`、`target_md5`、`target_sha256`、`target_head_revision_id`
- 资源关系：`resource_group_id`、`resource_kind`
- 状态：`status`、`failure_reason`、`retry_count`
- 时间：`started_at`、`uploaded_at`、`verified_at`
- 防篡改：`record_hash`，文件级 manifest 还要有 `manifest_sha256`

## 规则

只有 VerificationEngine 能把状态设置为 `VERIFIED_MATCH`。
