# Harness Setup Skill — 参考文档

## 各语言的规范领域对照表

本文档帮助 Skill 在 Phase 2 中决定为不同语言/框架的项目生成哪些规范。

---

## Go 项目规范领域

### P0（必须生成）

| 领域 | 文件名建议 | 检查项 |
|------|------------|--------|
| 错误处理 | `{project}_error.md` | error 返回值处理、错误包装（`%w`）、自定义错误类型、gRPC 错误转换 |
| 日志 | `{project}_log.md` | 日志库统一、级别选择、context 传递、敏感信息脱敏 |
| 项目结构 | `{project}_project_structure.md` | 分层规则、目录组织、依赖方向、模块间调用 |

### P1（推荐生成）

| 领域 | 文件名建议 | 检查项 |
|------|------------|--------|
| 数据库 | `{project}_db.md` | ORM 使用、查询规范、软删除、事务、分表 |
| API/Proto | `{project}_api.md` | gRPC/REST 命名、请求响应格式、版本管理 |
| 测试 | `{project}_test.md` | 表驱动测试、Mock 模式、覆盖率标准 |
| 并发 | `{project}_goroutine.md` | goroutine 管理、context 传递、sync 原语 |

### P2（按需生成）

| 领域 | 文件名建议 | 检查项 |
|------|------------|--------|
| 安全 | `{project}_security.md` | 输入校验、敏感数据、权限检查 |
| 缓存 | `{project}_cache.md` | key 命名、TTL、一致性策略 |
| 消息队列 | `{project}_mq.md` | Topic 命名、消费者规范、幂等 |
| 注释 | `{project}_comment.md` | 文件注释、函数注释、包注释 |

---

## Python 项目规范领域

### P0

| 领域 | 检查项 |
|------|--------|
| 错误处理 | try/except 粒度、自定义异常层级、异常日志 |
| 日志 | logging 配置、结构化日志、敏感信息 |
| 项目结构 | 包组织、层级依赖、circular import 防范 |

### P1

| 领域 | 检查项 |
|------|--------|
| 类型标注 | type hints 使用、mypy 配置 |
| 数据库 | SQLAlchemy/Django ORM 使用、migration 管理 |
| API | FastAPI/Flask 路由规范、Pydantic 模型 |
| 测试 | pytest fixture、parametrize、conftest 组织 |

---

## Node.js/TypeScript 项目规范领域

### P0

| 领域 | 检查项 |
|------|--------|
| 错误处理 | Error 类层级、async/await 错误捕获、全局错误处理 |
| 日志 | winston/pino 配置、请求 ID 追踪 |
| 项目结构 | 模块组织、barrel exports、依赖注入 |

### P1

| 领域 | 检查项 |
|------|--------|
| TypeScript | strict 模式、any 使用限制、类型导出 |
| API | Express/NestJS 路由、DTO 验证、中间件 |
| 测试 | Jest/Vitest 配置、mock 策略、E2E 测试 |

---

## Rust 项目规范领域

### P0

| 领域 | 检查项 |
|------|--------|
| 错误处理 | Result/Option 使用、thiserror/anyhow 选择、`?` 传播 |
| 项目结构 | crate 组织、mod 层级、pub 可见性 |

### P1

| 领域 | 检查项 |
|------|--------|
| 安全 | unsafe 使用审查、内存安全 |
| 并发 | Send/Sync trait、Arc/Mutex 模式 |
| 测试 | 单元测试（`#[cfg(test)]`）、集成测试、property testing |

---

## Java 项目规范领域

### P0

| 领域 | 检查项 |
|------|--------|
| 错误处理 | 异常层级（checked/unchecked）、全局异常处理 |
| 日志 | SLF4J/Logback 配置、MDC 上下文 |
| 项目结构 | Spring Boot 分层、包组织、Bean 管理 |

### P1

| 领域 | 检查项 |
|------|--------|
| 数据库 | JPA/MyBatis 使用、事务管理、分页查询 |
| API | Controller/Service/Repository 分层、DTO/VO 转换 |
| 测试 | JUnit 5、Mockito、Spring Boot Test |

---

## 审查维度模板

以下是 `/review` Skill 中使用的通用审查维度。根据项目实际生成的 Rules 选择适用的维度。

### 维度 1：架构合规

- 分层调用方向是否正确
- 是否有跨层/反向依赖
- 模块间是否通过导出接口交互

### 维度 2：错误处理

- error/exception 是否都被处理
- 错误转换模式是否符合规范
- 用户可见消息是否清晰

### 维度 3：日志规范

- 是否使用统一日志库
- 错误分支是否打印了日志
- 上下文（requestId 等）是否传递

### 维度 4：安全风险

- 是否有硬编码密钥
- 用户输入是否校验
- 敏感信息是否脱敏

### 维度 5：代码质量

- 函数是否过长
- 嵌套是否过深
- 是否有重复代码
- 命名是否清晰

### 维度 6：性能隐患

- 是否有 N+1 查询
- 是否在循环中做 I/O
- 是否有不必要的内存分配
