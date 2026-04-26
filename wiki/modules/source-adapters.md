# 源端适配器

来源：MDD-MOD-002、MDD-MOD-003、MDD-API-001、MDD-API-002。

## 模块

- `ICloudDriveSourceAdapter`
- `ICloudPhotosSourceAdapter`

## 输出

源端适配器不直接上传。它只输出：

- `TransferItem`
- 源端状态事件
- 可读取的字节流
- metadata snapshot

## 关键规则

- 不可读文件也必须输出状态，不得静默忽略。
- macOS Photos 使用 PhotoKit。
- Windows Photos 只当作目录媒体文件处理。
- package、Live Photo、RAW+JPEG 交给 ResourceNormalizer 统一处理。
