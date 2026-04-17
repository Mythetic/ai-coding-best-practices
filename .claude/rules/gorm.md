---
description: GORM usage standards - always active
globs:
  - "**/*.go"
---
你是一个专业的 Go 开发助手，所有 GORM 使用必须严格遵循以下规范。

**注意：本规范适用于项目的 GORM 使用，所有涉及数据库操作的场景必须遵守。项目已从 Beego ORM 迁移到 GORM，禁止在新代码中使用 Beego ORM。**

## ORM 框架引入

### 【必须】统一使用 GORM
- 必须使用 `gorm.io/gorm`，禁止引入 Beego ORM 或其他 ORM 框架
- 新增代码禁止使用 `github.com/astaxie/beego/orm` 或 `github.com/beego/beego/v2/client/orm`

## 查询规范

### 【必须】上下文传递
- 所有数据库操作必须调用 `WithContext(ctx)` 传递上下文

```go
db.WithContext(ctx).Where("id = ?", id).First(&user)
```

### 【必须】显式指定表名
- 所有操作必须通过 `Table()` 或 Model 的 `TableName()` 方法指定表名

### 【必须】记录不存在判断
- 使用 `errors.Is(err, gorm.ErrRecordNotFound)` 判断记录是否存在
- 禁止使用 Beego 的 `orm.ErrNoRows`

```go
// 单条查询
err := db.WithContext(ctx).Where("id = ?", id).First(&user).Error
if errors.Is(err, gorm.ErrRecordNotFound) {
    // 记录不存在
}
```

### 【必须】Find 与 First 的区别
- `First()`：查询单条记录，未找到时返回 `gorm.ErrRecordNotFound`
- `Find()`：查询多条记录，未找到时**不返回错误**，返回空切片
- 单条查询必须用 `First()`，禁止用 `Find()` 查单条（会丢失不存在的错误信号）

### 【推荐】只查询需要的字段
- 当表有大字段（text、blob）时，使用 `Select()` 指定需要的字段

```go
db.WithContext(ctx).Select("id", "name", "status").Where("org_id = ?", orgId).Find(&users)
```

### 【必须】防止 SQL 注入
- 必须使用占位符 `?` 传参，禁止字符串拼接 SQL

```go
// 正确
db.Where("name = ?", userName).Find(&users)

// 禁止
db.Where("name = '" + userName + "'").Find(&users)
```

## 写操作规范

### 【必须】插入操作
- 单条插入使用 `Create()`
- 批量插入使用 `CreateInBatches()`，每批不超过 100 条

```go
// 单条插入
err := db.WithContext(ctx).Create(&record).Error

// 批量插入
err := db.WithContext(ctx).CreateInBatches(records, 100).Error
```

### 【必须】更新操作 -- 使用 map 更新，禁止 struct 更新
- 更新参数必须使用 `map[string]interface{}`，禁止直接用 struct 更新（struct 会忽略零值字段）
- 更新使用 `Updates()` 或 `UpdateColumns()`

```go
// 正确：使用 map，零值字段也能正确更新
err := db.WithContext(ctx).Model(&User{}).Where("id = ?", id).
    Updates(map[string]interface{}{
        "name":       "newname",
        "age":        0,          // 零值也会被更新
        "updated_on": time.Now().Unix(),
    }).Error

// 禁止：struct 更新会忽略零值
err := db.WithContext(ctx).Model(&user).Updates(&user).Error
```

### 【必须】如需 struct 更新零值字段，使用 Select 显式指定

```go
err := db.WithContext(ctx).Model(&user).Select("Name", "Age").Updates(&user).Error
```

## 事务规范

### 【必须】使用 db.Transaction 自动管理事务
- 必须使用 `db.Transaction()` 方式，禁止手动 `Begin/Commit/Rollback`（容易遗漏回滚）

```go
err := db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
    if err := tx.Create(&record1).Error; err != nil {
        return err  // 自动回滚
    }
    if err := tx.Create(&record2).Error; err != nil {
        return err  // 自动回滚
    }
    return nil  // 自动提交
})
```

### 【必须】事务内使用 tx 而非 db
- 事务闭包内的所有操作必须使用回调参数 `tx`，禁止使用外部的 `db`

### 【必须】避免长事务
- 事务内禁止耗时操作（如外部 RPC 调用、文件 IO），只做数据库操作

## 批量操作规范

### 【必须】大批量插入使用 CreateInBatches
- 超过 10 条记录的批量插入必须使用 `CreateInBatches`，每批 100 条

### 【推荐】批量更新
- 批量更新使用 `Where` + `Updates`，避免循环单条更新

```go
db.WithContext(ctx).Model(&User{}).Where("id IN ?", ids).
    Updates(map[string]interface{}{"status": "active"})
```

## Upsert 规范

### 【推荐】使用 OnConflict 实现 InsertOrUpdate

```go
import "gorm.io/gorm/clause"

err := db.WithContext(ctx).Clauses(clause.OnConflict{
    Columns:   []clause.Column{{Name: "email"}},
    DoUpdates: clause.AssignmentColumns([]string{"name", "age"}),
}).Create(&user).Error
```

## 原生 SQL 规范

### 【推荐】优先使用 GORM 链式 API
- 能用链式 API 实现的查询，不使用原生 SQL

### 【必须】原生 SQL 必须使用参数化查询

```go
// 正确
db.WithContext(ctx).Raw("SELECT * FROM users WHERE age > ? AND status = ?", 18, "active").Scan(&users)

// 禁止
db.WithContext(ctx).Raw("SELECT * FROM users WHERE age > " + age).Scan(&users)
```

## 性能规范

### 【推荐】避免 N+1 查询
- 禁止在循环中执行单条查询，应使用批量查询或 `Preload`

```go
// 禁止：N+1 查询
for _, user := range users {
    db.WithContext(ctx).Where("user_id = ?", user.ID).Find(&orders)
}

// 正确：批量查询
db.WithContext(ctx).Where("user_id IN ?", userIds).Find(&orders)
```

### 【推荐】避免大 OFFSET 分页
- 大数据量分页禁止使用 `Offset(10000).Limit(100)`，应使用游标分页
