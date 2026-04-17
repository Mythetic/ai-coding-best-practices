---
description: Project module directory organization standards - always active
globs:
  - "**/*.go"
---
你是一个专业的 Go 开发助手，新增或修改代码时必须严格遵循以下项目模块目录组织规范。

**注意：本规范适用于项目的模块目录组织，所有新增模块、新增文件必须遵守。**

## 模块目录结构

### 【必须】标准模块目录结构

```
internal/<module_name>/
└── <version>/                # 版本目录（如 v1）
    ├── internal/             # 模块内部实现
    │     ├── api/            # gRPC API 注册与处理层
    │     ├── <module>client/ # 本地 gRPC 客户端包装层（如 certclient/）
    │     ├── logic/          # 核心业务逻辑封装（可按领域划分子目录）
    │     └── repository/     # 数据库操作层（也可命名为 db/）
    └── pkg/                  # 供其他模块调用的导出接口
          ├── boot/           # RPC 注册入口（仅转发到 internal/api/）
          ├── entity/         # 导出常量、枚举、类型（禁止依赖 internal 函数，也可命名为 model/）
          └── <其他导出包>/    # 按需导出（如 thirdparty/、encrypt/ 等）
```

### 【必须】版本目录
- 每个模块下必须包含版本目录（如 `v1/`），`internal/` 和 `pkg/` 位于版本目录内
- 完整路径示例：`internal/certificate/v1/internal/api/`

### 【推荐】扩展目录（按需添加）

`internal/` 下可按需添加：`cmd/`、`base/`、`callback/`、`consumer/`、`entity/`、`library/`、`policy/`、`evidence/`、`logical/`、`mocks/`、`encrypt/` 等按领域划分的子目录

### 实际示例

```
internal/
├── certificate/v1/                          # 证书模块
│   ├── internal/
│   │   ├── api/                             # gRPC API 层
│   │   │   └── certificate_service.go
│   │   ├── certclient/                      # 客户端包装层
│   │   │   ├── cert_client.go
│   │   │   └── certificate_interface.go
│   │   ├── logic/                           # 业务逻辑（按领域划分子目录）
│   │   │   ├── provider/
│   │   │   ├── parser/
│   │   │   ├── utils/
│   │   │   ├── creator/
│   │   │   ├── factory/
│   │   │   └── thirdparty/
│   │   └── repository/                      # 数据库操作层
│   └── pkg/
│       ├── boot/
│       ├── entity/
│       └── thirdparty/
├── hello/v1/                                # 示例模块
│   ├── internal/
│   │   ├── api/
│   │   ├── db/                              # 数据库操作层（命名为 db）
│   │   └── logic/
│   └── pkg/
│       ├── boot/
│       └── model/                           # 导出类型（命名为 model）
└── secureuser/v1/                           # 安全用户模块（按领域划分）
    ├── internal/
    │   ├── encrypt/
    │   ├── algorithm/
    │   ├── manager/
    │   └── fingerprint/
    └── pkg/
        ├── encrypt/
        ├── entity/
        └── manager/
```

## 分层职责规范

### 【必须】各层职责

| 层 | 职责 | 要点 |
|------|------|------|
| `api/` | gRPC 注册与请求处理 | 只做参数校验和转发，不含业务逻辑 |
| `<module>client/` | 本地 gRPC 客户端包装 | `Set` + `New` 模式管理服务实例 |
| `logic/` | 核心业务逻辑 | 可按领域划分子目录，禁止依赖 API 层 |
| `repository/` 或 `db/` | 数据库操作 | 只含数据访问逻辑，不含业务逻辑 |

### 【必须】导出层（pkg）

- `pkg/boot/`：仅转发到 `internal/api/` 的注册函数
- `pkg/entity/`（或 `pkg/model/`）：导出常量和类型，禁止依赖 `internal/` 函数
- `pkg/<其他导出包>/`：按需提供客户端接口、工具函数等

## 模块间调用规范

### 【必须】调用方式

- 同进程 -> 通过目标模块 `pkg/` 下的导出包获取本地客户端
- 独立进程 -> gRPC 远程调用

### 【必须】分层调用规则

api、logic、repository 三层之间严格分层，调用链路必须为 **api -> logic -> repository**，逐层向下单向依赖，禁止跨层或反向调用。

- **api 层**：仅负责参数校验、协议解析和调用 logic，不包含任何业务逻辑或数据库操作
- **logic 层**：承载核心业务逻辑，通过调用 repository 完成数据读写，禁止直接依赖 api 层
- **repository 层**：仅封装数据库访问操作，不包含业务判断，不感知上层调用者


### 【必须】依赖方向

```
✓ moduleA/v1/internal/logic/ → moduleB/v1/pkg/entity/
✓ moduleA/v1/internal/logic/ → moduleA/v1/internal/repository/
✗ moduleA/v1/internal/ → moduleB/v1/internal/（禁止跨模块依赖 internal）
✗ moduleA/v1/pkg/entity/ → moduleA/v1/internal/logic/（entity 禁止依赖 internal 函数）
```

## 核心设计原则

1. **同类业务聚合**：高内聚，相关业务放同一模块
2. **pkg 规范对外接口**：只保留需要对外暴露的包
3. **internal 内部自由**：内部实现可按领域灵活组织（如 `encrypt/`、`fingerprint/` 等）
4. **版本化管理**：模块通过版本目录（`v1/`）管理演进
5. **依赖注入**：通过构造函数注入依赖
