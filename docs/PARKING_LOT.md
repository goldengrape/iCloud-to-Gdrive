# PARKING_LOT / 暂存但不进入 MVP 的内容

这些内容有价值，但当前不进入 MVP，避免需求过宽。

## PARK-001 自动删除 iCloud 数据

后续版本可以研究，但必须满足：公开稳定接口、单独权限、重新校验、单独 deletion manifest、不可清空最近删除。

## PARK-002 Google Photos 迁移

当前目标是 Google Drive，不是 Google Photos。Google Photos 的相册、人物、回忆和搜索语义另开项目。

## PARK-003 文件格式转换

Pages/Numbers/Keynote 转 PDF 或 Office 格式可能有用，但会改变原始内容表达。MVP 只做原样备份或 package 压缩。

## PARK-004 Manifest 本地签名

MVP 使用 record_hash + manifest_sha256。后续可支持本地密钥签名、时间戳服务或导出校验器。

## PARK-005 全量扫描 Google Drive 去重

需要更高权限或更复杂的 Picker 授权，不进入 MVP。
