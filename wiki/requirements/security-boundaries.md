# 安全边界

来源：URD-REQ-001、URD-REQ-002、URD-REQ-013、URD-CON-001、URD-CON-002、MDD-INV-001、MDD-INV-003。

## 不允许

- 不要求 Apple ID 密码。
- 不要求 Apple 2FA 验证码。
- 不通过网页模拟登录 iCloud。
- 不把文件内容上传到第三方中转服务器。
- 不把 token 写入普通日志。
- 不在 MVP 中调用删除接口。

## 允许

- 读取用户本机已授权的 iCloud 数据。
- 使用 Google OAuth 获取 Drive 写入权限。
- 读取字节流用于上传和哈希计算。
- 在本地保存任务状态和 manifest。

## 实现提示

SecurityBoundary 应作为独立模块存在。其他模块需要保存 token 时必须通过系统安全存储接口。
