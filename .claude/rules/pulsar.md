---
description: Message queue (Pulsar) standards - always active
globs:
  - "**/*.go"
---
你是一个专业的后台开发助手，所有消息队列（MQ）相关的 Topic、消费者订阅等设计必须严格遵循以下规范。

**注意：本规范适用于项目的消息队列设计，所有 Topic 创建、消费者订阅等操作必须遵守。**

## Topic 命名规范

### 【必须】Topic 命名规则
- 格式：`{服务名}-{模块名}-{业务名}-topic`
- 各部分用 `-` 连接，业务名中多个单词用 `_` 连接
- 服务名：如 `user-service`、`billing-service`、`order-service` 等
- 模块名：如 `flow`、`order`、`template`、`document`、`payment` 等

示例：`order-service-payment-create_order-topic`

## 消费者订阅命名规范

### 【必须】消费者订阅名称
- 格式：`{服务名}-{模块名}-{内部业务}-consumer`
- 各部分用 `-` 连接，内部业务名中多个单词用 `_` 连接

示例：`order-service-message-order_create-consumer`
