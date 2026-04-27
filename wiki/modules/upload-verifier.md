# 上传与校验

来源：URD-REQ-014、URD-REQ-015、URD-REQ-019、MDD-MOD-005、MDD-MOD-006、MDD-MOD-008。

## 上传规则

- 小于 5MB：允许 multipart upload。
- 大于 5MB：必须 resumable upload。
- session URI 和 confirmed offset 必须持久化。
- 恢复上传时必须查询服务端 Range，不能假设上次发送的字节全部成功。

## 校验规则

- 源端读取时同时计算 MD5 和 SHA-256。
- 目标端有 sha256Checksum：用 SHA-256 判定。
- 目标端无 SHA-256 但有 MD5：用 MD5 判定，保留源端 SHA-256。
- checksum 都没有：只能弱校验，不得标记 VERIFIED_MATCH。

## 错误处理

- 429、403 rate limit、5xx：退避重试。
- 配额或存储不足：进入暂停状态并提示用户。
- session 过期：重新创建 session，保留失败记录。


## 冲突规则

来源：URD-REQ-016、TDD-TEST-013、TDD-TEST-014。

只有强校验一致才能自动跳过同名目标文件。`VERIFIED_WEAK` 不能作为 `SKIPPED_ALREADY_EXISTS` 的依据，也不能进入清理候选。
