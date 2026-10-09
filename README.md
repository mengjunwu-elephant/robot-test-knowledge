# 大象机器人软件测试知识库

公共知识 + 项目独立知识 + 共享 Codex Skills，版本 0.1.0。
本仓库已创建为本地目录；应用侧项目登记与远程仓库尚未完成。

- standards/：公共约束及 Git 同步流程。
- fundamentals/：可观察结果、证据与边界设计。
- skills/：两项共享技能的唯一维护源。
- .agents/skills/：本仓库可发现的同步副本；不要单独修改。
- projects/：三个项目的证据索引、字段快照与差异说明；实际用例继续在各自项目维护。
- templates/：接口契约、用例变更、测试生成审查和项目接入模板。
- scripts/：离线校验、固定 Git 提交同步及自测。
- docs/：方案总文档与唯一项目交接文档。

离线执行：`python scripts/validate_offline.py`；`python scripts/test_sync.py`。
来源校验：`python scripts/validate_offline.py --sources`，只读比较三个原项目。

试用：在目标项目调用 `$testcase-iteration` 或 `$pytest-generation`，明确项目、接口、来源文件、Excel Sheet 和范围。首次使用必须重新读取目标项目当前规则，不依赖本仓库快照替代现场事实。
同步示例详见 [Git 同步](standards/git-sync.md)。这两个技能是工作流技能，不是无人审核的硬件测试生成器。

官方技能目录依据：https://learn.chatgpt.com/docs/build-skills 。未注册远程服务、未上传源项目、未安装全局技能。
