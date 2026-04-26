# 校验测试

来源：TDD-TEST-010、TDD-TEST-011、TDD-TEST-012、TDD-TEST-015、TDD-TEST-018。

## 必测规则

1. SHA-256 可用时优先 SHA-256。
2. 只有 MD5 可用时使用 MD5。
3. checksum 不可用时只能弱校验。
4. manifest 必须记录强校验依据。
5. 清理列表展示前必须重新复核目标文件。

## 失败条件

- 目标无 checksum 但状态为 VERIFIED_MATCH。
- CSV 有记录但 JSON manifest 没有对应记录。
- 清理列表包含目标端已删除或 revision 已变化的项目。
