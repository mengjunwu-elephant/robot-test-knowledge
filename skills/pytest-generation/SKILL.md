---
name: pytest-generation
description: 依据已确认用例和项目源码生成或修改单接口 pytest 测试，保护 Fixtures、Allure、Excel 参数化和恢复逻辑。
---

# 单接口pytest编写与维护

先读[团队公共规则](references/team-rules.md)，再读[自动化测试契约](references/automation-contract.md)。技能版本0.7.0；实际加载版本须核对安装清单，旧对话不会因仓库更新自动升级。

## 1. 确认任务和项目

读取当前AGENTS、规则、用例技能、目录conftest、Excel loader、邻近单接口测试和源码证据，按[项目差异](references/project-context.md)重新定位。

明确新增或修改哪些接口，已确认用例范围及允许的生成、静态检查、collection或执行阶段。资料不足先列缺口，不生成猜测性调用。需要新方案才提出至少三个收敛问题并取得“确认执行”；已授权范围不重复确认。

## 2. 接口与数据契约

- 核对真实签名、异常类型、单位、范围、返回及预期依据。
- 核对fixture、数据路径、Sheet、字段、参数化身份、marker及恢复责任。
- SDK的title单行参数化与ROS的automation_id分别处理，不复制跨项目SDK规则。

## 3. 实现与维护

以邻近单接口测试为骨架，保留函数名、fixture scope、Allure、日志、marker、skip、ID和原调用顺序。调用、等待、结构断言、业务断言、回读和恢复直接可见，不新增连接或万能Executor/Adapter。

异常使用已证实类型，raises块外记录exc.value，双臂按当地契约分别捕获。setter先快照原值、try/finally恢复并回读；恢复失败显式暴露，等待有超时。不猜运动姿态或限位。

## 4. 验证与交付

授权的静态检查用AST验证语法，不导入目标模块；对比Excel与源码映射及变更，说明不能静态证明的行为。collection需要明确授权和导入副作用审查，本知识库不运行来源项目collection或设备测试。

输出修改副本、差异、依据、检查结果及未验证项。静态通过不能报告实机通过；新方案更新总文档，任务完成更新唯一交接及相关规则技能。
