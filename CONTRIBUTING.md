# 团队维护
1. 测试人员从 main 创建分支，修改 skills、standards 或模板，提交 PR，说明依据、前后差异与离线验证结果。
2. 公共规则修改同步两项技能 references/team-rules.md；技能修改同步 .agents/skills。不得提交原始 Excel、密钥、连接地址或现场日志。
3. @mengjunwu-elephant 审核，检查项目兼容性，合并后执行发布工作流。新版本必须提高 plugin.json 版本并更新 CHANGELOG。
4. 发布工作流只在指定维护者手动执行时发布；Windows/Linux 校验通过才能生成正式 Release。成员更新只取最新正式 Release。
5. 维护者自己的修改也走 PR；单维护者无法审批自己的 PR，需其他获授权审核者或明确记录管理员应急合并。新增维护者须同时更新 CODEOWNERS、发布白名单和 GitHub 保护设置。
