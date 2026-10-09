# Git 版本化共享

公共仓库维护通用流程，原项目维护 docs/knowledge 与现有规则；公共库的 projects 只保存差异和来源索引。不能把原项目私有规则向所有产品推广。

每个发布版本先离线校验，再提交并标记版本。远程平台、地址与权限尚待确认，本轮不推送。
技能采用固定提交导出，不跟随浮动分支：
`python scripts/sync_skills.py --repo . --revision <完整40位提交> --target <项目根>`
默认只预览。加 `--apply` 安装到目标 `.agents/skills/`；默认拒绝覆盖同名技能。输出 `knowledge.lock.json`，记录提交、路径、SHA256。升级时先核对旧 lock 和本地技能哈希，再在独立分支移走已核对的旧副本、重新导出并 review，不自动覆盖本地编辑。
同步仅含 skills 下两项包，不写目标 AGENTS、Excel、conftest 或已有其他技能。
回滚：在项目 Git 分支中恢复上次提交的技能与 lock，校验哈希。远程拉取只获取 Git 内容，不自动安装或执行代码。
本仓库 `.agents/skills` 是 skills 的相同副本，validate_offline 验证二者一致；任何修改须同步两个位置后提交。
