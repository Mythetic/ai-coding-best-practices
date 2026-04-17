---
description: Goroutine usage standards - always active
globs:
  - "**/*.go"
---
你是一个专业的 Go 开发助手，所有 goroutine 使用必须严格遵循以下规范。

**注意：本规范适用于项目的 goroutine 使用，所有涉及 `go func()` 启动异步协程的场景必须遵守。**

## Goroutine 启动规范

### 【必须】使用安全封装函数启动 goroutine

启动 goroutine 时，**必须**使用项目封装的 `base.Go(func())` 替代原生 `go func()`，禁止直接使用 `go` 关键字启动协程。

**原因**：`base.Go` 内部自动 `recover` panic 并发送告警通知，防止野生 goroutine panic 导致进程崩溃。直接使用 `go` 关键字启动的协程如果发生 panic，会导致整个进程退出。

```go
// 正确：使用 base.Go 启动，自动捕获 panic
base.Go(func() {
    // ... 业务逻辑 ...
})
```

**反例**：

```go
// 禁止：直接使用 go 关键字，panic 会导致进程崩溃
go func() {
    // ... 业务逻辑 ...
}()
```

## Context 处理规范

### 【必须】goroutine 内部使用脱离 cancel 的 context

启动 goroutine 时，**必须**使用 `context.WithoutCancel(ctx)` 创建新的 context 传入，禁止直接使用外部传入的 ctx。

**原因**：外部 ctx 可能携带 timeout 或上层 cancel 信号，一旦外层请求结束，ctx 被取消后会导致 goroutine 内部的数据库操作、RPC 调用等全部失败。`context.WithoutCancel` 会创建不受父 context cancel 影响的子 context，同时保留所有 context value（包括链路追踪信息 TraceId、RequestId 等）。

### 【必须】context 脱离 cancel 的方式选择

| 方式 | 说明 | 适用场景 |
|------|------|----------|
| `context.WithoutCancel(ctx)` | Go 1.21+ 标准库方法，保留所有 context value，去除 cancel 信号 | 绝大部分场景 |
| `base.CopyCtx(ctx)` | 基于 `context.Background()` 创建新 context，仅保留链路追踪信息 | **推荐使用**，需要完全隔离上游 context 的场景 |

### 【必须】完整示例

```go
// 正确：使用 base.CopyCtx 脱离 cancel + base.Go 启动
newCtx := base.CopyCtx(ctx)
base.Go(func() {
    err := doSomething(newCtx)
})
```

**反例**：

```go
// 禁止：使用了 base.Go 但未脱离 cancel，外层请求结束后 ctx 会被 cancel
base.Go(func() {
    err := doSomething(ctx)
})
```
