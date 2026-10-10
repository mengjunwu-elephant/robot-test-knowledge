---
name: pytest-generation
description: 依据已确认用例和项目源码生成或修改单接口 pytest 测试，保护 Fixtures、Allure、Excel 参数化和恢复逻辑。
---


用例编写与自动化编写/自检分开授权。仅要求编写、完善或评审用例时，不开展pytest源码审查、数据映射检查、AST自检、collection或执行；可阅读必要SDK源码核实接口事实。历史试用意向不代表当前自动化授权。明确要求自动化后，区分生成、静态检查、collection和执行范围，静态检查授权不等于运行授权。
# pytest-generation

先读取并遵循 [团队公共规则](references/team-rules.md)。本技能版本0.6.0；Codex/Work通过安装目录Update.cmd更新正式版，Cursor通过插件来源刷新/更新。更新后开启新对话；离线时报告当前版本，不能声称已是最新版或将分支刷新当成正式版锁定。

读取目标当前 AGENTS、规则、用例技能、目录 conftest、Excel loader、代表测试与接口源码证据；读取 [项目差异参考](references/project-context.md) 定位差异。
确认接口签名、fixture、数据路径、Sheet、字段、ID、异常类、断言与恢复契约。资料不完整则完成缺口清单，不生成猜测性可执行调用。
以邻近单接口用例为骨架；调用、等待、断言、回读与恢复直接写在测试函数。禁止新增连接、万能 Executor/Adapter 或跨项目 SDK 规则。
保留函数名、fixture scope、marker、skip、Allure、日志风格与参数化 ID；SDK 单行 title 装饰器与 ROS automation_id 分开处理。
异常用具体已证实类型，raises 块外记录 exc.value；双臂分别捕获。setter 按当地规则先快照，再 try/finally 恢复。
生成后用 AST 检查 Python 语法且不导入目标模块，比较 Excel 与源码差异。collection 仅在已确认无导入连接后执行；本知识库任务不运行来源项目 collection。
未确认运动姿态、SDK 契约与预期不可填猜值。离线静态通过不能报告为实机通过。更新方案总文档、唯一交接文档与受影响规则技能。
