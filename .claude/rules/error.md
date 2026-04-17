---
description: Error handling standards - always active
globs:
  - "**/*.go"
---
你是一个专业的 Go 开发助手，所有错误处理必须严格遵循以下规范。

**注意：本规范适用于项目的错误处理，使用项目内置错误处理库 `transform`。**

> 说明：下方示例中的 `transform` 和 `errorcode` 包路径需根据实际项目替换为真实的 import 路径。

## 错误处理库引入

### 【必须】统一使用项目错误处理库
- 必须使用项目统一的 `transform` 错误处理库
- 错误码使用项目统一的 `errorcode` 常量包
- 禁止使用 `fmt.Errorf`、`errors.New`、`grpc/status` 直接返回给 gRPC 调用方

## 错误返回函数规范

### 【必须】错误返回函数选择

| 函数 | 说明 | 适用场景 |
|------|------|----------|
| `transform.Simple(msg, code)` | 简单错误返回 | 本层直接产生的业务错误 |
| `transform.SimpleFromError(baseErr, msg, code)` | 链式错误返回 | 串联上游(gRPC/transform)返回的 error |
| `transform.Advance(msg, code, desc)` | 详细错误返回（不告警） | 需要区分用户消息和研发描述 |
| `transform.AdvanceSimple(msg, code)` | Advance 简化版（不告警） | 同 Advance 但无需额外描述 |

### 【必须】`transform.Simple` -- 本层直接产生的业务错误

```go
// 参数校验 / 数据不存在 / 数据库操作失败等本层判定的错误
if flow == nil {
    return transform.Simple("未找到指定的签署流程",  errorcode.ErrNotExistResource)
}
```

### 【必须】`transform.SimpleFromError` -- 串联上游错误

```go
// 调用其他 gRPC 服务或已用 transform 封装的函数，需追加本层信息
err := someapi.CallCheckResourceValid(ctx, orgId, resourceId)
if err != nil {
    log.Err("call CheckResourceValid fail").Ctx(ctx).Error(err).Json()
    return transform.SimpleFromError(err, "资源校验失败",
    errorcode.ErrNoPermission)
}
```

- `baseErr` 为 nil 时直接返回 nil
- `code` 传空字符串则优先使用上游错误码

### 【推荐】`transform.Advance` / `transform.AdvanceSimple` -- 不触发告警

```go
// 区分用户消息和研发描述，不触发机器人告警
return transform.Advance("PDF合成超时，可能是文件过大导致", errorcode.ErrSystem, "PDF合成超时，重试3次失败")

// 无需研发描述时用简化版
return transform.AdvanceSimple("未找到生成的文档信息", errorcode.FailedOperation)
```

## 错误透传规则

### 【必须】透传 vs 串联决策

- 上游已用 `transform` 封装且本层不需修改 -> **直接 `return err`**
- 上游错误需追加本层信息 -> **`transform.SimpleFromError`**
- 本层直接产生的错误 -> **`transform.Simple`**

## 错误消息规范

### 【必须】用户可见消息（msg）
- 使用中文描述，面向用户，简洁说明问题和建议操作
- 避免暴露内部技术细节
- 少用"系统错误，请稍后重试"类似的错误，尽量简要的写明原因和指导处理方式

### 【必须】错误码（code）
- 尽量使用 `errorcode` 包中的常量，禁止硬编码字符串
- 错误码应与错误类型匹配
- 少用"InternalError"错误

## 错误处理与日志配合

### 【必须】日志 + 错误返回配合
- 有 `err` 对象时，返回 `transform` 错误前**必须先打印错误日志**
- 纯业务判断（如 nil 检查）无 err 对象时可直接返回

```go
// 有 err：先打日志再返回
if err != nil {
    log.Err("call DescribeResource fail").Ctx(ctx).Error(err).Json()
    return nil, transform.Simple("查询资源失败", errorcode.ErrSystem)
}

// 无 err 且场景明确：直接返回
if activeInfo == nil {
    return "", nil, transform.Simple("未找到企业激活信息,请确认是否已授权",
    errorcode.OrganizationNotAuthorized)
}
```

### 【必须】上游错误码提取
根据上游错误码做分支处理时，使用 `errorutil.GetErrorCode` 提取：

```go
if err := flowOperation.ExecuteFlow(ctx, flowId); err != nil {
    errorCode, _ := errorutil.GetErrorCode(err)
    if errorCode == errorcode.ReviewNotPass {
        log.Inf("review not pass, skip").Ctx(ctx).Error(err).Json()
    } else {
        log.Err("call ExecuteFlow fail").Ctx(ctx).Error(err).Json()
        return err
    }
}
```
