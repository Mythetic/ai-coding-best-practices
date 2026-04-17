---
description: Protobuf definition standards - always active
globs:
  - "**/*.proto"
---
你是一个专业的后台开发助手，所有 Protobuf 定义必须严格遵循以下规范。

**注意：本规范适用于项目的 Protobuf 接口定义，所有 `.proto` 文件必须遵守。**

> 说明：下方示例中的 package、go_package、java_package 路径需根据实际项目替换为真实路径。

## 语法与包规范

### 【必须】基本声明
- 必须使用 `proto3` 语法
- `package` 格式：`grpc.{项目名称}.{资源名称}.v1`（小写纯英文，点分隔）
- `go_package` 格式：`{项目仓库}/api/{项目名称}/{资源名称}/v1`
- 必须声明 Java 选项：
  - `java_multiple_files = true`
  - `java_package` 格式：`com.{组织}.{项目名称}.api.{资源名称}.v1`
  - `java_outer_classname` 格式：`{资源名称:驼峰}Proto`
- 必须引入公共依赖（根据项目实际情况配置）

文件头模板：

```protobuf
syntax = "proto3";

package grpc.{项目名称}.{资源名称}.v1;

option go_package = "{项目仓库}/api/{项目名称}/{资源名称}/v1";

option java_multiple_files = true;
option java_package = "com.{组织}.{项目名称}.api.{资源名称}.v1";
option java_outer_classname = "{资源名称:驼峰}Proto";

// 根据项目需要引入公共依赖
```

示例（项目名称=certificate，资源名称=hello）：

```protobuf
syntax = "proto3";

package grpc.certificate.hello.v1;

option go_package = "example.com/myproject/api/certificate/hello/v1";

option java_multiple_files = true;
option java_package = "com.example.myproject.api.certificate.hello.v1";
option java_outer_classname = "HelloProto";
```

### 【必须】文件存放路径
- 路径格式：`proto/{模块名称(可省略)}/{资源名称}/{版本}/{资源名称}.proto`
- 文件名小写，与资源名称一致
- 完整示例文件可参考：`proto/hello/v1/hello.proto`

### 【必须】目录结构

```
proto/
├── {模块名称(可省略)}/
│   └── {资源名称}/
│       └── {版本}/
│           └── {资源名称}.proto
```

示例：

```
proto/
├── hello/
│   └── v1/
│       └── hello.proto
├── say/
│   └── v1/
│       └── say.proto
└── merchant/
    ├── shop/
    │   └── v1/
    │       └── shop.proto
    └── staff/
        └── v1/
            └── staff.proto
```

- 当模块下只有单一资源时，可省略模块名称层级（如 `proto/hello/v1/`）
- 当模块下有多个资源时，使用模块名称作为上级目录（如 `proto/merchant/shop/v1/`）

## 服务定义规范

### 【必须】Service 命名
- 大驼峰命名，必须以 `Service` 结尾，如 `FlowService`、`SealService`

## 方法定义规范

### 【必须】RPC 方法命名
- 大驼峰命名，**动词 + 资源名** 模式，长度不超过 64 字符
- 英文全拼，禁止缩写和拼音

| 操作 | 动词前缀 | 禁止使用 |
|------|----------|----------|
| 创建 | `Create` | ~~Get、Add~~ |
| 删除 | `Delete` | ~~Remove~~ |
| 修改 | `Modify` | ~~Update~~ |
| 查询 | `Describe` | ~~Get~~ |

- 批量接口用 `List` 后缀（如 `DescribeDNSList`），不用 `s`/`es`
- 内部接口必须加 `Inner` 前缀，Request/Response 也带 `Inner`

### 【必须】请求和响应类型
- 请求：`方法名 + Request`，响应：`方法名 + Response`
- 必须为独立 message，禁止复用

## HTTP 映射规范

### 【推荐】网关映射
- 路径：`/gw/{方法名}`，统一 `post`，`body: "*"`

### 【必须】API 映射
- 路径：`/api:{方法名}`

## Message 与字段规范

### 【必须】Message 命名
- 大驼峰命名，清晰表达含义

### 【必须】字段命名
- **snake_case** 命名，全拼不缩写（`id`、`url`、`pdf` 等广泛缩写除外）
- 每个字段必须有注释

### 【必须】字段编号
- 从 `1` 开始递增，已发布接口禁止修改编号
- 废弃字段用 `reserved` 保留编号

### 【推荐】字段类型选择

| 场景 | 类型 |
|------|------|
| 资源 ID | `string` |
| 时间戳 | `int64` |
| 状态值 | `enum` |
| 列表 | `repeated` |
| 坐标/尺寸 | `double` |
| 页码/计数 | `int32` |
| 布尔标志 | `bool` |

## 通用参数命名规范

### 【必须】分页参数

| 参数 | 命名 | 备注 |
|------|------|------|
| 偏移量 | `offset` | 配合 `limit`，从 0 开始 |
| 限制数目 | `limit` | 配合 `offset` |
| 页码 | `page_number` | 配合 `page_size` |
| 每页数目 | `page_size` | 配合 `page_number` |
| 总数目 | `total_count` | 响应中返回 |
| 过滤 | `filters` / `filter` | 标注精确/模糊匹配 |
| 列表 | `xxx_set` | 如 `flow_set`，不用 `flows` |

### 【必须】字符串常量
- 常量取值一律**大写 + 下划线**（如 `AUTO_RENEW`）

## 版本管理规范

### 【必须】向后兼容
- 禁止删除、重命名已有字段
- 禁止修改已有字段的编号和类型
- 新增字段必须使用新编号
