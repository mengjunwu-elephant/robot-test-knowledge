# 知识库维护规则

仅用于维护robot-test-knowledge仓库，不随技能作为日常测试规则加载。

## 维护源与目录

- skills是两项技能唯一维护源，.agents/skills为内容相同的发现镜像。不得直接改个人plugins/cache。
- 公共底线维护standards/team-rules.md，同步两技能references/team-rules.md；自动化契约维护standards/testing-contract.md，同步pytest-generation/references/automation-contract.md。
- Cursor清单引用现有skills，不另建技能源。项目独立知识在原项目维护，projects只保留来源与差异索引。
- 文档分使用、维护、验收示例；总方案及交接保持唯一、表达当前状态。舍弃设计及历史过程通过Git查阅。

## 团队审核

- 普通成员建分支提PR，说明依据、差异及验证，由@mengjunwu-elephant审核。
- 维护者本人及明确授权代提交免人工审批，但仍完成必要检查；其他成员不享有此例外。
- 新增维护者须同步CODEOWNERS、发布白名单和远程保护配置。不因main推送自动发布。

## 打包与发布

- 以plugin.json、skills和明确白名单打包，禁止项目快照、原工作簿、密钥及现场配置进入安装包。
- 版本同步根/Cursor清单、技能及维护的版本提示，更新CHANGELOG。不得用同版本覆盖正式资产或移动旧标签。
- 发布由维护者手动触发；Windows/Linux隔离检查通过才发布正式Release。安装器保留原来源条目和备份，拒绝同名外部来源及被修改的同版本。
- Windows入口改动实际验证成功/失败路径，临时user-root隔离；命令避免replacement string的$语义，错误窗口保留说明及日志路径。

## 安装、更新与同步

- Codex/Work的Install.cmd与Update.cmd登记个人来源；来源登记不等于客户端已加载，新对话前需刷新插件。
- Cursor走其来源刷新；分支刷新不等于只跟随正式Release。客户端显示/调用未验证时如实记录。
- 正式包更新与固定完整提交的项目导出分别处理，详见[Git同步规范](git-sync.md)。不自动覆盖用户改动。

## 检查与交付

按改动运行离线完整性、安装/更新、相关结构/格式/同步回归；技能结构验证不代替行为试用。测试不写真实个人目录，不导入设备模块。更新方案总文档、唯一交接及变更记录，分别说明源码状态、正式版本和本机状态。
