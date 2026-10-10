# 大象机器人软件测试知识库

测试团队共同维护的公共规则、项目差异知识及两项共享技能。当前正式版本 **v0.6.0**。更新日期：2026-10-10。

## 从这里开始

- 第一次安装：[安装指南](docs/使用/技能包安装指南.md)。
- 日常使用：[团队使用步骤](docs/使用/团队使用步骤.md)、[用例编写操作](docs/使用/用例编写技能使用.md)。
- 能做什么、验证到哪一步：[能力说明](docs/使用/使用维护与能力说明.md)。
- 修改与发布：[迭代维护](docs/维护/技能包迭代维护.md)、[贡献规则](CONTRIBUTING.md)。
- 已验收写法：[夹爪验收](docs/验收示例/夹爪v1.4.1/夹爪v1.4.1-六项问题修订验收.md)。
- 当前建设与接续：[方案总文档](docs/方案总文档.md)、[唯一交接文档](docs/项目交接文档.md)。

## 当前两项技能

**testcase-iteration：用例编写与迭代。**读取实际需求、接口资料和已有工作簿，先确认Sheet范围，再评审接口测试点、确认完整方案，最后生成副本。保留原字段、编号、历史结果、公式和批准格式。前置写必要状态，步骤写真实调用或人工动作，预期逐步对应；不凑行数或猜接口契约。

**pytest-generation：自动化编写与维护。**依据已确认用例和当前项目源码新增或修改单接口pytest。读取现有数据加载、Fixtures和邻近测试，保护参数化ID、Allure、marker、skip及恢复逻辑。生成和维护需要人工审查；静态校验不代表设备验证通过。

目前仅维护这两项技能。用例遗漏和预期依据检查在现有工作流中完成，再交人工评审；不再独立建设缺陷分析、覆盖审查或测试报告技能。

## 安装与更新

正式资产见[GitHub发布页](https://github.com/mengjunwu-elephant/robot-test-knowledge/releases/latest)。下载robot-test-knowledge-0.6.0.zip并完整解压，或下载同版本单文件安装入口；GitHub Source code ZIP不是安装包。

Codex/Work：运行Install.cmd完成个人来源登记，在客户端刷新个人来源并安装/启用插件，开启新对话。更新运行安装目录Update.cmd，再刷新插件并开启新对话。来源登记成功不等于当前对话已经加载新版；不要直接改plugins/cache。

Cursor：从GitHub插件入口导入本仓库，安装后新开对话选择技能。更新走其插件来源入口；Install.cmd/Update.cmd只用于Codex/Work。仓库来源可能跟踪分支，不声称只跟随正式Release。支持情况以实际客户端为准。

若在线更新遇GitHub限流，改从正式发布页下载包安装。旧版保留；同名外部来源或已修改的版本遇冲突时安装器停止，不自动覆盖。

## 对话示例

用例：“使用testcase-iteration，完善本项目xxx工作簿。先读现有规则和协议，列Sheet范围和测试点供确认，再输出方案与副本，保留字段，不运行自动化。”

自动化：“使用pytest-generation，依据已确认用例完善xxx接口测试。先读取现有fixture、数据和接口契约，输出修改副本及差异，只做授权的静态检查，不连接设备。”

提供产品、模块、完整版本、资料位置及实际工作簿。资料不足时先列具体缺口；源码的当前行为不能独自证明正确业务预期。

## 目录职责

```text
robot-test-knowledge/
├─ AGENTS.md / CONTRIBUTING.md / CHANGELOG.md
├─ README.md / plugin.json
├─ standards/       公共流程、测试与Git规范
├─ fundamentals/    测试设计与证据原则
├─ skills/          两项技能唯一维护源
├─ .agents/skills/  同内容发现镜像
├─ .cursor-plugin/  Cursor入口，引用skills
├─ templates/       项目接入、契约、变更及审查记录
├─ projects/        项目差异和来源索引
├─ examples/        可复用演示，实际结果不可照抄
├─ docs/
│  ├─ 使用/         安装、日常操作、能力边界
│  ├─ 维护/         反馈、迭代与发布
│  ├─ 验收示例/     当前验收及必要追溯
│  ├─ 方案总文档.md
│  ├─ 项目交接文档.md
│  └─ 目录与文档整理方案.md
├─ scripts/         同步、离线检查、打包及回归
└─ packaging/       安装更新入口与隔离验证记录
```

仓库根离线JSON为脚本生成的最近检查记录，不是业务测试结果。dist是忽略的本地构建目录，不作为共享知识入口。项目真实SDK、协议及现场配置在原项目维护；公共索引需按当前分支和版本重新核对。

## 维护与检查

成员从main建分支并提PR，@mengjunwu-elephant审核发布；维护者本人或明确授权代提交免人工审批。维护源是skills，修改需同步.agents/skills；公共规则修改按既有维护流程同步。不能把项目成功码、运动常量和连接信息推广到所有项目。

常规验证从仓库根执行：

```powershell
python -X utf8 scripts/validate_offline.py
python -X utf8 scripts/test_package.py
python -X utf8 scripts/test_update.py
```

根据改动运行结构/格式/同步等相关回归。安装入口改动另验证双击成功和失败路径，使用临时用户目录。发布同步根/Cursor版本及技能版本，更新CHANGELOG，通过Windows/Linux工作流后生成新的Release；不覆盖旧资产。

## 已验证和仍需完善

v0.6.0正式发布通过Windows/Linux安装、更新、同步、结构和格式回归。夹爪266条副本已获用户写法与结构验收，10条缺API及协议/测量判据仍待补；未运行设备测试。自动化技能还需在真实项目验证生成与维护效果。

本轮只整理仓库目录和文档，正式v0.6.0下载资产与两技能内容保持原样。业务Excel、原项目、安装包保留。删除的设计及过程文档可查Git历史，不作为当前工作入口。


未发布优化：用例审查明确四项交付，格式工具按团队通用基线识别字段并支持项目配方；夹爪仅是示例。已安装v0.6.0尚不包含此修订。


## 规则阅读入口

- [公共规则](standards/team-rules.md)：所有测试任务的依据、授权、保护及诚实交付底线。
- [用例技能](skills/testcase-iteration/SKILL.md)：编写确认、测试点、写法、通用格式及四项审查。
- [自动化技能](skills/pytest-generation/SKILL.md)：单接口编写维护、断言、恢复及验证。
- [仓库维护规则](standards/repository-maintenance.md)：只供维护者处理镜像、审核、打包和发布。

公共规则及流程重构为仓库未发布修订；已安装v0.6.0需等待新版发布并更新，不把仓库当前规则当成已安装内容。
