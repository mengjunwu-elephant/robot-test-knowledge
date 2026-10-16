---
name: pytest-generation
description: 依据已确认用例和项目源码生成或修改单接口 pytest 测试，保护 Fixtures、Allure、Excel 参数化和恢复逻辑。
---

# 单接口pytest编写与维护

先读[团队公共规则](references/team-rules.md)，再读[自动化测试契约](references/automation-contract.md)。正式v0.8.2的基础流程沿用v0.8.1；当前仓库新增堵转与进行中参考及适用条件，尚未发布。记录安装清单版本及来源：包内build-info.json的渠道、提交和内容指纹；仓库来源记录Git提交与未提交状态。客户端无法给出提交时记录未知及当前SKILL文件哈希，不只凭版本号判定内容。旧对话不会因仓库更新自动升级。

按当前任务查看[经验入口](references/pitfalls/index.md)，只读匹配短记录，不加载全部历史或扩大授权。

## 1. 确认任务和项目

读取当前AGENTS、规则、用例技能、目录conftest、Excel loader、邻近单接口测试和源码证据，按[项目差异](references/project-context.md)重新定位。

明确新增或修改哪些接口，已确认用例范围及允许的生成、静态检查、collection或执行阶段。资料不足先列缺口，不生成猜测性调用。需要新方案才提出至少三个收敛问题并取得“确认执行”；已授权范围不重复确认。

## 2. 按任务读取方法

读取[数据分类与证据](references/data-and-evidence.md)。直接SDK调用读取[SDK场景](references/sdk-patterns.md)；ROS Service/Topic读取[ROS场景](references/ros-patterns.md)。用例出现堵转，或运动中、运行中、校准中、校准时、校准过程、校准过程中、校准进行、运行过程中、回零过程中、回零中、回零时及相同意思时，读取[堵转与进行中场景](references/in-progress-and-stall.md)，按其中弹窗和接口调用顺序生成。按项目实际调用模型选择，不以项目名称替代事实判断，不全量套用两个模式。

这些参考提炼自Tuya规则及抽样源码，现有源码含未完成断言/恢复和旧展示标题，不能整文件照抄。原项目专属值仍按当前契约核对；仅查询、普通设置和异常的设计方法，不提供运动执行模板。

## 3. 接口与数据契约

- 核对真实签名、异常类型、单位、范围、返回及预期依据。
- 核对fixture、数据路径、Sheet、字段、参数化身份、marker及恢复责任。
- SDK的title单行参数化与ROS的automation_id分别处理，不复制跨项目SDK规则。

## 4. 实现与维护

先核对邻近单接口测试的断言与恢复是否完整，再借其结构，保留函数名、fixture scope、Allure、日志、marker、skip、ID和原调用顺序。调用、等待、结构断言、业务断言、回读和恢复直接可见，不新增连接或万能Executor/Adapter。

异常使用已证实类型，raises块外记录exc.value，双臂按当地契约分别捕获。setter先快照原值、try/finally恢复并回读；恢复失败显式暴露，等待有超时。不猜运动姿态或限位。

## 5. 验证与交付

授权的静态检查用AST验证语法，不导入目标模块；对比Excel与源码映射及变更，说明不能静态证明的行为。collection需要明确授权和导入副作用审查，本知识库不运行来源项目collection或设备测试。

交付前按[生成与维护复核](references/generation-acceptance.md)核对真实业务断言、数据映射和恢复，不把pass/字段存在当业务完成。输出修改副本、差异、依据、检查结果及未验证项。静态通过不能报告实机通过；新方案更新总文档，任务完成更新唯一交接及相关规则技能。
