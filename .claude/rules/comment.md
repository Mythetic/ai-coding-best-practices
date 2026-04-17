---
description: Code comment standards - always active
globs:
  - "**/*.go"
---
你是一个专业的 Go 开发助手，所有代码注释必须严格遵循以下规范。

**注意：本规范适用于项目的代码注释风格，所有导出函数、方法的注释必须遵守。**

## 注释总则

### 【必须】注释 Why 不注释 What
- 注释应解释**业务约定**和**边界条件**，不注释显而易见的代码逻辑
- 读代码的都是高级工程师，CRUD 逻辑、参数校验、nil 判断等不需要逐行注释

## 导出函数注释规范

### 【必须】函数功能 + 入参出参说明
- 每个导出函数必须有注释，第一行为函数功能简述，格式：`// 函数名 功能描述`
- 紧跟其后，使用 `//   - 参数名: 说明` 格式逐项描述入参
- 返回值使用 `//   - 返回值: 说明` 格式描述，重点说明边界情况（如"不存在时返回 nil"、"未找到的不会出现在 map 中"）
- 只对类型不明显或有业务约定的参数做说明（如"传空表示清除"、"为空时跳过"）
- 显而易见的 `ctx context.Context` 无需注释

示例：
// DescribeFlowLogo 查询流程标图Logo
//   - flowId: 签署流程ID
//   - 返回值: Logo URL，不存在时返回空字符串
func DescribeFlowLogo(ctx context.Context, flowId string) (string, error) {
