---
name: "Beego to GORM Migration"
description: 将 Beego ORM 代码迁移为 GORM 代码，支持指定文件或目录批量转换
category: 迁移工具
tags: [migration, beego, gorm, orm, refactor]
---

将指定文件或目录中的 Beego ORM 代码迁移为 GORM，遵循项目规范。

**输入**：`/beego2gorm` 之后的参数是要转换的文件路径、目录路径，或模块名。

- 文件路径：`/beego2gorm internal/template/internal/repository/template_component_repo.go`
- 目录路径：`/beego2gorm internal/template/internal/repository/`
- 模块名：`/beego2gorm template`
- 无参数：交互式询问目标

---

## 步骤

### 1. 确定转换目标

如果提供了路径或模块名，直接使用。否则使用 **AskUserQuestion tool** 询问：
> "请提供要迁移的文件路径、目录路径或模块名"

如果是目录或模块名，扫描其中所有包含 Beego ORM 用法的 `.go` 文件（排除 `_test.go`），列出文件清单让用户确认。

### 2. 分析现有 Beego ORM 代码

逐文件分析，识别以下 Beego ORM 使用模式：

**ORM 实例获取**
- `GetOrmByModel(new(Model))` / `GetOrmInstance()`
- `ormInstance.QueryTable()`

**Model 结构体标签**
- `orm:"pk"` / `orm:"auto"` / `orm:"column(xxx)"` 等

**查询操作**
- `qs.Filter("field", value)` / `qs.Filter("field__gte", value)` — 双下划线语法
- `qs.One(&result)` / `qs.All(&results)`
- `qs.Count()`
- `qs.OrderBy("-created_at")` — 减号降序
- `qs.Limit()` / `qs.Offset()`
- `qs.Exclude("field", value)`

**写操作**
- `ormInstance.Insert(&record)` / `ormInstance.InsertMulti()`
- `ormInstance.Update(record, "Field1", "Field2")`
- `ormInstance.Delete(&record)`
- `ormInstance.InsertOrUpdate(record, "conflict_field")`
- `qs.Update(orm.Params{...})` — 批量更新

**事务**
- `o.Begin()` / `o.Commit()` / `o.Rollback()` — 手动事务

**错误处理**
- `err == orm.ErrNoRows` / `err == orm.ErrMissPK`

**原生 SQL**
- `ormInstance.Raw(sql).QueryRow()` / `.QueryRows()`
- `ormInstance.Raw(sql).Exec()`

### 3. 按以下规则执行转换

#### 3.1 ORM 实例替换

```
// Beego
ormInstance, _ := GetOrmByModel(new(Model))

// GORM — 根据 Model 对应的数据库选择正确的 GetGOrm* 函数
db := register.GetGOrmDefault()  // 或项目中对应的数据库实例获取函数
```

**数据库实例选择**：查看原代码中 `GetOrmByModel` 传入的 Model 对应的数据库分组，选择对应的数据库实例获取函数。如果无法确定，询问用户。

#### 3.2 Model 结构体标签转换

| Beego Tag | GORM Tag |
|-----------|----------|
| `orm:"pk"` | `gorm:"primaryKey"` |
| `orm:"auto"` | `gorm:"autoIncrement"` |
| `orm:"column(xxx)"` | `gorm:"column:xxx"` |
| `orm:"size(100)"` | `gorm:"size:100"` |
| `orm:"null"` | `gorm:"default:null"` |
| `orm:"unique"` | `gorm:"uniqueIndex"` |
| `orm:"index"` | `gorm:"index"` |

同时确保 Model 实现了 `TableName()` 方法，表名定义为包级私有常量。

#### 3.3 查询条件转换

| Beego Filter | GORM Where |
|--------------|------------|
| `Filter("field", value)` | `Where("field = ?", value)` |
| `Filter("field__gt", value)` | `Where("field > ?", value)` |
| `Filter("field__gte", value)` | `Where("field >= ?", value)` |
| `Filter("field__lt", value)` | `Where("field < ?", value)` |
| `Filter("field__lte", value)` | `Where("field <= ?", value)` |
| `Filter("field__contains", value)` | `Where("field LIKE ?", "%"+value+"%")` |
| `Filter("field__startswith", value)` | `Where("field LIKE ?", value+"%")` |
| `Filter("field__in", slice)` | `Where("field IN ?", slice)` |
| `Filter("field__isnull", true)` | `Where("field IS NULL")` |
| `Exclude("field", value)` | `Not("field = ?", value)` |

**注意**：Beego Filter 中的字段名是 Go struct 字段名（大驼峰），转换后 Where 中使用数据库列名（蛇形）。

#### 3.4 查询方法转换

```
// 单条查询
qs.One(&result)                → db.WithContext(ctx).First(&result).Error
// 判断不存在
err == orm.ErrNoRows           → errors.Is(err, gorm.ErrRecordNotFound)

// 多条查询
qs.All(&results)               → db.WithContext(ctx).Find(&results).Error
// 注意: Find 查不到不返回错误

// 计数
qs.Count()                     → db.WithContext(ctx).Model(&Model{}).Count(&count).Error

// 排序
qs.OrderBy("created_at")       → Order("created_at ASC")
qs.OrderBy("-created_at")      → Order("created_at DESC")

// 分页
qs.Limit(10).Offset(20)        → Limit(10).Offset(20)
```

#### 3.5 写操作转换

```
// 单条插入
ormInstance.Insert(&record)           → db.WithContext(ctx).Create(&record).Error

// 批量插入
ormInstance.InsertMulti(n, records)    → db.WithContext(ctx).CreateInBatches(records, 100).Error

// 指定字段更新 — 必须使用 map，禁止 struct 更新
ormInstance.Update(record, "F1","F2")  → db.WithContext(ctx).Model(&Model{}).Where("id = ?", id).
                                           Updates(map[string]interface{}{"f1": v1, "f2": v2}).Error

// 批量更新
qs.Update(orm.Params{"status":"x"})   → db.WithContext(ctx).Model(&Model{}).Where(...).
                                           Update("status", "x").Error

// Upsert
ormInstance.InsertOrUpdate(r, "email") → db.WithContext(ctx).Clauses(clause.OnConflict{
                                             Columns:   []clause.Column{{Name: "email"}},
                                             DoUpdates: clause.AssignmentColumns([]string{...}),
                                         }).Create(&record).Error

// 删除 — 项目禁止物理删除，转为软删除
ormInstance.Delete(&record)           → db.WithContext(ctx).Model(&Model{}).Where("id = ?", id).
                                           Updates(map[string]interface{}{
                                               "is_deleted": 1,
                                               "deleted_on": time.Now().Unix(),
                                           }).Error
```

#### 3.6 事务转换

```
// Beego 手动事务
o := orm.NewOrm()
o.Begin()
// ...操作...
o.Commit() / o.Rollback()

// GORM 自动事务
db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
    // ...操作使用 tx 而非 db...
    return nil  // 自动提交；返回 error 自动回滚
})
```

#### 3.7 原生 SQL 转换

```
// Beego
ormInstance.Raw(sql, args...).QueryRow(&result)
ormInstance.Raw(sql, args...).QueryRows(&results)
ormInstance.Raw(sql, args...).Exec()

// GORM
db.WithContext(ctx).Raw(sql, args...).Scan(&result)
db.WithContext(ctx).Raw(sql, args...).Scan(&results)
db.WithContext(ctx).Exec(sql, args...)
```

#### 3.8 Import 替换

```
// 移除
"github.com/astaxie/beego/orm"
"github.com/beego/beego/v2/client/orm"

// 新增
"gorm.io/gorm"
"gorm.io/gorm/clause"              // 如有 Upsert
```

### 4. 转换后检查

对每个转换后的文件执行以下检查：

- [ ] 所有数据库操作都添加了 `WithContext(ctx)`
- [ ] 所有更新操作使用 `map[string]interface{}`，无 struct 更新
- [ ] 错误判断使用 `errors.Is(err, gorm.ErrRecordNotFound)`
- [ ] 事务使用 `db.Transaction()` 而非手动 Begin/Commit
- [ ] 无 SQL 字符串拼接
- [ ] import 已清理，无残留 Beego ORM 引用
- [ ] 日志和错误处理符合项目规范

### 5. 输出转换报告

转换完成后，输出简要报告：

```
## 转换报告

**文件**: xxx_repo.go
**转换项**:
- ORM 实例: GetOrmByModel → register.GetGOrmDefault()
- 查询: 3 处 Filter → Where
- 更新: 2 处 Update → Updates(map)
- 错误处理: 1 处 orm.ErrNoRows → gorm.ErrRecordNotFound
- 事务: 1 处手动事务 → db.Transaction
- Import: 清理 beego orm，新增 gorm

**需要人工确认**:
- [如有不确定的转换，列出]
```

---

## 补充场景

### 场景 A：DAO 层整体重构

当转换涉及整个 repository 文件时，除了逐行转换 ORM 调用，还应：

1. **检查是否需要重构为 struct 接收器模式**：如果原代码是包级函数直接调用 `GetOrmByModel`，考虑改为带 `*gorm.DB` 字段的 DAO struct，通过构造函数注入。
2. **统一 TableName**：确保表名常量和 `TableName()` 方法存在。
3. **分表逻辑**：如果原代码有分表（按年月或哈希），保留分表计算逻辑，用 `Table(tableName)` 指定表名。

### 场景 B：跨层调用迁移

如果原代码在 logic 层直接调用了 `GetOrmByModel`（违反分层规范）：

1. 将数据库操作下沉到 repository 层
2. logic 层通过调用 repository 函数完成数据访问
3. 顺便修正分层依赖

### 场景 C：公共封装函数迁移

如果原代码使用了旧版 db 包的封装函数（如 `db.InsertDb`、`db.UpdateDb`、`db.ReadDb`）：

```
// 旧封装
db.InsertDb(ctx, &record)         → gormDb.WithContext(ctx).Create(&record).Error
db.UpdateDb(ctx, &record)         → gormDb.WithContext(ctx).Model(&Model{}).Where("id = ?", id).
                                       Updates(map[string]interface{}{...}).Error
db.ReadDb(ctx, &record, "Id")     → gormDb.WithContext(ctx).Where("id = ?", id).First(&record).Error
db.InsertOrUpdate(ctx, &r, "col") → gormDb.WithContext(ctx).Clauses(clause.OnConflict{...}).Create(&r).Error
```

---

## 护栏

- **不要遗漏 WithContext(ctx)**：这是最常见的遗漏项
- **不要用 struct 更新**：零值陷阱是 GORM 最常见的 bug
- **不要保留 Beego import**：转换后文件不应有任何 Beego ORM 引用
- **不确定时询问用户**：特别是 ORM 实例选择（对应哪个数据库）和分表逻辑
- **保持函数签名不变**：转换只改内部实现，不改对外接口（除非用户明确要求）
- **遵循项目规范**：转换后的代码必须符合 gorm、error、log、mysql 等规范
