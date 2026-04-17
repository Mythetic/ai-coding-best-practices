---
description: Resource ID generation standards - always active
globs:
  - "**/*.go"
---
你是一个专业的 Go 开发助手，所有资源/实体的 ID 生成必须严格遵循以下规范。

**注意：本规范适用于项目的资源 ID 生成，所有涉及资源唯一标识（非数据库自增主键 `id`）的场景必须遵守。**

> 说明：下方示例中的 `id` 包路径需根据实际项目替换为真实的 import 路径。

## ID 生成库引入

### 【必须】统一使用项目 ID 生成库
- 必须使用项目统一的 ID 生成库

引入示例：
```go
import (
    "example.com/myproject/library/id"
)
```

## ID 生成函数规范

### 【必须】ID 生成函数选择

项目 `id` 包提供以下 ID 生成函数，按使用场景选择：

| 函数 | 说明 | 适用场景 |
|------|------|----------|
| `id.GetNewId()` | 生成资源唯一 ID（无需 context） | 不依赖 context 的场景，如初始化、简单赋值 |
| `id.GetId(ctx)` | 生成资源唯一 ID（需要 context） | 有 context 的业务逻辑中，推荐使用此方法 |

### 【必须】`id.GetNewId()` -- 无 context 场景

当函数签名中**没有 `context.Context` 参数**，或在初始化等无 context 的场景下，使用 `id.GetNewId()` 生成资源 ID：

```go
// 无 context 时使用 GetNewId
resourceId, err := id.GetNewId()
if err != nil {
    log.Err("get new id fail").Error(err).Line()
    return transform.Simple("系统错误，请稍后重试", errorcode.ErrSystem)
}
```

### 【必须】`id.GetId(ctx)` -- 有 context 场景

当函数签名中**有 `context.Context` 参数**时，推荐使用 `id.GetId(ctx)` 生成资源 ID：

```go
// 有 context 时推荐使用 GetId
flowInstanceId, err := id.GetId(ctx)
if err != nil {
    log.Err("get id fail").Ctx(ctx).Error(err).Line()
    return transform.Simple("系统错误，请稍后重试", errorcode.ErrSystem)
}
```
