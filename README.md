# 大象机器人软件测试知识库

公共知识 + 项目独立知识 + 共享 Codex Skills，版本 0.2.0。
本仓库已创建为本地 Git 项目；远程地址为 https://github.com/mengjunwu-elephant/robot-test-knowledge 。应用侧项目登记仍需完成。

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

官方技能目录依据：https://learn.chatgpt.com/docs/build-skills 。远程只同步本知识库内容；未上传源项目原始工作簿、未安装全局技能。

使用前请阅读 [使用、维护与实际能力](docs/使用维护与能力说明.md)，区分已验证能力、工作流支持和规划。

## 可安装技能包（本地已生成，远程待发布）

本地离线入口在 outputs/robot-test-knowledge-0.2.0-Install.cmd，双击登记个人来源后重启桌面应用，在插件目录安装。GitHub 连接无写权限，v0.2.0 尚未发布；桌面实际安装与 Python 运行测试未验收。此来源安装适用于支持本地插件的桌面客户端，未发布到公共商店。

[安装与使用步骤](docs/技能包安装指南.md)。包内含用例迭代、pytest 生成两个技能；plugin.json 为打包入口。应用实际安装/技能调用待现场验收，不把静态打包成功视为功能调用通过。

安装后的更新流程见[技能包迭代维护](docs/技能包迭代维护.md)。
