# 团队维护
1. 测试人员从 main 创建分支，修改 skills、standards 或模板，提交 PR，说明依据、前后差异与离线验证结果。
2. 公共规则修改同步两项技能 references/team-rules.md；技能修改同步 .agents/skills。可共享用户授权且经过内容检查的模板与资料；不得提交密钥、连接地址或敏感现场日志。
3. @mengjunwu-elephant 审核，检查项目兼容性，合并后执行发布工作流。新版本必须提高 plugin.json 版本并更新 CHANGELOG。
4. 发布工作流只在指定维护者手动执行时发布；Windows/Linux 校验通过才能生成正式 Release。成员更新只取最新正式 Release。
5. @mengjunwu-elephant 自己提交或明确授权代为提交的修改免人工审批，可直接提交或合并；仍需通过必要校验。其他测试人员修改继续走 PR，由维护者审核。当前 main 对管理员允许绕过审批，此权限仅授权仓库所有者用于自己的修改，不代表其他成员免审。新增维护者须同时更新 CODEOWNERS、发布白名单和 GitHub 保护设置。
