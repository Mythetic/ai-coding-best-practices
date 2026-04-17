---
description: Logging standards - always active
globs:
  - "**/*.go"
---
你是一个专业的 Go 开发助手，所有日志打印必须严格遵循以下规范。

**注意：本规范适用于项目的日志记录，使用项目内置日志库。**

> 说明：下方示例中的 `log` 包路径需根据实际项目替换为真实的 import 路径。

## 日志库引入

### 【必须】统一使用项目日志库
- 必须使用项目统一的日志库
- 禁止使用标准库 `log`、`fmt.Println`、第三方日志库（`logrus`、`zap` 等）

## 日志级别规范

### 【必须】日志级别选择

| 级别 | 方法 | 适用场景 |
|------|------|----------|
| Debug | `log.Deb(msg)` | 开发调试信息、详细中间状态 |
| Info | `log.Inf(msg)` | 请求响应、业务流程追踪、性能耗时 |
| Warn | `log.War(msg)` | 潜在问题预警、降级处理、可恢复异常 |
| Error | `log.Err(msg)` | 操作失败、数据库异常、外部调用失败 |

### 【必须】错误日志要求
- 所有 `error != nil` 分支必须打印错误日志
- 错误日志必须附加 `.Error(err)` 携带原始错误信息
- 禁止有 err 但不打印就返回

## 链式调用规范

### 【必须】核心链式方法

| 方法 | 说明 | 是否必须 |
|------|------|----------|
| `.Error(err)` | 附加错误对象 | 错误日志必须 |
| `.Ctx(ctx)` | 附加请求上下文（自动提取 requestId/logId 等链路信息） | 有 ctx 时必须 |
| `.Str(key, val)` | 附加字符串键值对 | 按需 |
| `.Any(key, val)` | 附加任意类型键值对 | 按需 |
| `.Line()` / `.Json()` | 输出格式 | 必须 |

> 还提供 `.Strs()`、`.Int()`、`.Float()`、`.Bool()`、`.Duration()`、`.Time()` 等类型方法，底层均调用 `.Any()`，可提升可读性。

### 【必须】上下文传递
- 函数签名有 `context.Context` 时，日志必须调用 `.Ctx(ctx)`

### 【推荐】链式调用顺序

```
log.Err/Inf/War/Deb(msg).Error(err).Ctx(ctx).Str/Any(key, val)...Json()
```

## 日志消息规范

### 【必须】消息内容要求
- 使用简短描述，中英文均可，不加标点结尾
- 日志库会**自动追加** `[函数名]: ` 前缀，禁止在消息中重复写函数名

### 【推荐】消息命名风格
- 操作类：`动词 + 名词 + 结果`，如 `"fill pdf err"`、`"update doc err"`
- 流程类：`名词 + 描述`，如 `"resource response"`
- 入口/出口：函数名，如 `"convertFormsIdForFill end"`

## 关键信息记录规范

### 【必须】错误场景附加信息
- 错误日志应附加关键业务 ID 辅助排查

```go
log.Err("desc resource err").Error(err).Ctx(ctx).Str("ResourceId", docu.ResourceIds).Json()
```

### 【推荐】键名命名
- 键名使用**大驼峰（PascalCase）**，如 `"FlowId"`、`"DocumentId"`、`"Response"`

## 性能日志规范

### 【推荐】耗时统计
- 关键操作（RPC、数据库、PDF 合成等）推荐 `defer` + `time.Since`

```go
st := time.Now()
defer func() {
    log.Inf(fmt.Sprintf("callPdfFill cost[%s]", time.Since(st))).Ctx(ctx).Json()
}()
```

## 日志安全规范

### 【必须】敏感信息脱敏
- 禁止打印密码、密钥、Token、身份证号、手机号等敏感信息

### 【必须】日志量控制
- 禁止在循环体内打印大量日志
- 避免将超大对象直接写入日志
