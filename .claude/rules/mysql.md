---
description: MySQL database design standards - always active
globs:
  - "**/*.go"
  - "**/*.sql"
---
你是一个专业的数据库开发助手，所有 MySQL 表定义和字段设计必须严格遵循以下规范。

**注意：本规范适用于项目的 MySQL 数据库设计，所有建表、改表操作必须遵守。**

## 字符集规范

### 【必须】统一字符集
- 所有数据库和表必须使用 `utf8mb4` 字符集

## 命名规范

### 【必须】数据库名
- 建议以统一前缀开头（如 `app_`），其它规则同表名

### 【必须】表名
- 小写字母 + 下划线分隔，名词复数，全拼不缩写，禁用系统保留词
- 必须与 PB、API 定义一致
- 正确：`users`、`flow_documents`、`seal_policies`

### 【必须】字段名
- 小写字母 + 下划线分隔，名词单数，全拼不缩写，禁用系统保留词
- 必须与 PB、API 定义一致
- 正确：`id`、`user_id`、`policy`、`description`

## 设计原则

### 【必须】禁止项
- 不做复杂计算（逻辑在程序中完成）
- 不使用存储过程、视图、外键
- 时间字段一律由程序端生成，转为 int 时间戳后写入数据库；禁止在 SQL 或表定义中使用 Now()、CURRENT_TIMESTAMP、ON UPDATE CURRENT_TIMESTAMP 等数据库自动取时函数。
- 禁止使用like操作

### 【必须】主键
- 采用 `AUTO_INCREMENT` 自增 `bigint` 类型

## 公共字段规范

### 【必须】建表模板

```sql
CREATE TABLE IF NOT EXISTS `table_names` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `resource_id` char(32) NOT NULL DEFAULT '' COMMENT '业务唯一ID',
  # ......业务用字段......
  `creator` char(32) NOT NULL DEFAULT '' COMMENT '创建者',
  `updater` char(32) NOT NULL DEFAULT '' COMMENT '修改者',
  `is_deleted` tinyint(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT '状态, 0-可用,1-不可用',
  `created_on` int(11) COMMENT '创建时间',
  `updated_on` int(11) COMMENT '更新时间',
  `deleted_on` int(11) COMMENT '删除时间',
  PRIMARY KEY (`id`),
  KEY `resource_id`(`resource_id`)
) ENGINE = InnoDB CHARSET = utf8mb4 COMMENT = '表描述';
```

## 禁止操作规范

### 【必须】禁止删表和清表
- 禁止 `DROP TABLE`、`TRUNCATE TABLE`
- 废弃表用 `RENAME TABLE xxx TO xxx_drop`，备份表加 `_bak` 后缀

## ORM 框架规范

### 【必须】统一使用 GORM
- 只能使用 `gorm.io/gorm`，禁止引入其他 ORM 框架

### 【必须】Model 结构体定义
- 字段名大驼峰，GORM 自动转蛇形映射
- 主键加 `gorm:"primaryKey"` 标签，非数据库字段加 `gorm:"-"`
- 必须实现 `TableName()` 方法，表名定义为包级私有常量

```go
const sealTableName = "seals"

type Seals struct {
    Id         string `gorm:"primaryKey"`
    SealName   string
    ResourceId string
    IsDeleted  int8
}

func (*Seals) TableName() string { return sealTableName }
```

### 【必须】查询规范
- 所有操作必须 `WithContext(ctx)` + `Table()` 显式指定表名
- 所有查询默认添加 `is_deleted = 0` 条件

### 【必须】写操作规范
- 创建用 `Create()`，更新用 `UpdateColumns()` / `Updates()`
- 更新参数用 `map[string]interface{}`，禁止 struct 更新（避免零值问题）
- 禁止物理删除，必须软删除（更新 `is_deleted` + `deleted_on`）

### 【必须】记录不存在判断
- 使用 `gorm.ErrRecordNotFound` 判断

## 分表规范

### 【必须】禁止使用 gorm/sharding 插件
- 分表逻辑由程序实现：计算分表名 -> `Table(tableName)` 指定

### 【必须】按年月分表
- 年月从 `resource_id` 中提取：`id.GetMonth(resourceId)` -> `YYYYMM`
- 分表名格式：`{原表名}_{年月}`

```go
func getTableName(resourceId string) string {
    date := id.GetMonth(resourceId)
    if date < "202301" {
        return ""
    }
    return fmt.Sprintf("%s_%s", baseTableName, date)
}
```

### 【可选】按哈希分表
- 分表名格式：`{原表名}_{分片编号}`，通过分表键哈希取模计算

```go
func getShardTableName(shardingKey string) string {
    hash := crc32.ChecksumIEEE([]byte(shardingKey))
    return fmt.Sprintf("%s_%d", baseTableName, hash%numberOfShards)
}
```

### 【推荐】按业务领域划分子目录

```
repository/
├── user/               # 用户相关
├── auth/               # 授权相关
├── resource/           # 资源管理
└── cache/              # 缓存层
```
