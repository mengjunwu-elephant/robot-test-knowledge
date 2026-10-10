# 知识库工作规则

## 开始任务

先检索目标项目已有AGENTS.md、.cursorrules、.agents/skills、.cursor/skills及.codex规则，读取与当前任务相关的文件。读取本库[团队公共底线](standards/team-rules.md)；维护本仓库时再读取[仓库维护规则](standards/repository-maintenance.md)。

## 根据任务选择入口

- 用例编写、迭代或审查：读取[testcase-iteration](skills/testcase-iteration/SKILL.md)。完整审查须分别完成结构、格式、内容和视觉检查，并如实说明范围；团队格式不依赖夹爪名称。
- 自动化生成或维护：读取[pytest-generation](skills/pytest-generation/SKILL.md)，不因用例任务自动触发。
- 同步、安装、发布：按仓库维护规则、[贡献流程](CONTRIBUTING.md)和相应脚本；两项技能以外不新增独立规划。

## 授权与记录

需要新方案时先提出至少三个问题，取得“确认执行”后保存P0/P1/P2方案并同步[方案总文档](docs/方案总文档.md)。已授权范围不重复确认，任务完成更新[唯一交接](docs/项目交接文档.md)。

本知识库不连接机器人、不运行来源项目测试或collection。原项目文件只读，编辑产生副本并保护原结构；共享业务文件逐项核对，不批量上传。当前明确指令决定范围，历史任务授权不延伸至新任务。
