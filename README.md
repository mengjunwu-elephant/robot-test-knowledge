# 大象机器人测试知识库

供测试团队维护公共规则、项目差异和两项共享技能。当前正式版本为 **v0.8.2**；本仓库新增的堵转/进行中规则、审查工具修复及安装诊断尚未发布。合并源码不会自动更新已安装插件，具体内容以提交号或包内 `build-info.json` 为准。

## 先选任务

- **审查已有用例**：使用 `testcase-iteration`，提供工作簿、Sheet 范围和可信资料。默认检查结构、格式、内容、视觉四项；报告实际范围与未验证项，不修改原件。
- **编写或迭代用例**：使用 `testcase-iteration`，先确认 Sheet 范围，再评审测试点和完整方案，确认后生成副本。保留模板、字段、编号、公式与历史记录。
- **生成或维护自动化**：使用 `pytest-generation`，提供已确认用例、接口契约和目标项目路径。复用现有 Fixtures、参数化、Allure 及恢复逻辑，区分生成、静态检查和执行授权。

资料至少包括产品/模块、完整软件或固件/SDK 版本、实际文件位置及预期依据。源码只能说明当前实现，不能独自证明业务预期正确；缺少接口、返回值、状态时序或恢复依据时明确待确认。

## 安装与更新

### Codex / Work

1. 从[正式发布页](https://github.com/mengjunwu-elephant/robot-test-knowledge/releases/latest)下载完整 ZIP 并解压，或下载同版本的单文件 Windows 安装入口。GitHub 自动生成的 Source code ZIP 不是安装包。
2. Windows 需 Python 3.10 或以上，运行 `Install.cmd` 登记个人插件来源。
3. 重启应用，刷新个人来源，安装/启用插件，再开启新对话确认实际加载的版本。
4. 更新时运行安装目录的 `Update.cmd`，或下载新正式包运行其中的 `Install.cmd`，随后刷新插件并新开对话。在线更新受限时使用正式发布页手动下载。

来源登记成功不代表当前对话已加载新版。旧版本保留；同名外部来源或被修改的同版本会被拒绝覆盖。Windows 安装路径过长时，安装器在写入前停止并提示选择较短的 `--user-root`；该目录仍须对应客户端实际读取的个人来源位置。详见[安装指南](docs/使用/技能包安装指南.md)。

### Cursor

从 GitHub 插件入口导入本仓库，更新走 Cursor 的来源刷新入口；`Install.cmd` / `Update.cmd` 用于 Codex / Work。仓库来源可能跟踪分支，内容不一定等于最新正式 Release，须记录实际提交或技能文件哈希。客户端支持和实际加载效果分别验证。

## 日常使用

审查示例：

> 使用 testcase-iteration，审查本项目 xxx.xlsx 的指定 Sheet，按团队基线与批准的项目差异检查结构、格式、内容和视觉，说明实际检查范围与缺口，不修改原件、不连接设备。

编写示例：

> 使用 testcase-iteration，完善指定版本的用例，先列实际 Sheet 和接口测试点供确认，明确每个环境的操作、观察对象和预期行为，再生成保留模板结构的副本。

自动化示例：

> 使用 pytest-generation，依据已确认用例维护 xxx 接口测试，先读当前规则、Fixtures、数据加载和真实接口契约，输出差异及恢复逻辑，只做静态检查。

已授权范围不重复确认。新方案按项目规则收敛并确认；用例编写授权不等于自动化或设备执行授权。

## 能力与验证边界

两项技能由助手结合当前项目资料使用，不是脱离项目的一键测试程序。结构工具支持三类模板及批准的字段布局，格式工具默认采用团队基线；未知字段、漏列和排除项会标明。静态检查不能替代内容、视觉或真实业务验收。

- 公共规则、镜像、打包、隔离安装、更新和固定提交同步有离线回归；正式 v0.8.2 有 Windows/Linux 发布校验记录。
- 夹爪 266 条副本获得写法与结构验收，仍有 10 条缺 API 入口及协议/测量判据待补，不代表设备通过。
- 自动化有纯内存 SDK/Service 模拟与故障探测。真实项目生成维护效果、客户端加载和设备行为仍需各自验收。
- 堵转与进行中场景按本条批准前置生成；进行中还需核验接口返回语义及状态有效时机，不能把“接口已返回”当作“设备仍在运行”。未知时不生成猜测性流程。

不在本知识库连接机器人、运行来源项目 collection 或设备测试；未执行不填 Pass，不直接编辑个人 `plugins/cache`。

## 文档入口

- 使用：[团队使用步骤](docs/使用/团队使用步骤.md)、[用例编写操作](docs/使用/用例编写技能使用.md)、[能力说明](docs/使用/使用维护与能力说明.md)。
- 规则：[团队公共底线](standards/team-rules.md)、[用例技能](skills/testcase-iteration/SKILL.md)、[自动化技能](skills/pytest-generation/SKILL.md)。
- 接入：[AGENTS 片段](templates/项目接入-AGENTS片段.md)、[项目固定提交同步](standards/git-sync.md)。
- 维护：[贡献流程](CONTRIBUTING.md)、[仓库维护规则](standards/repository-maintenance.md)、[技能包迭代](docs/维护/技能包迭代维护.md)。
- 当前进展：[方案总文档](docs/方案总文档.md)、[唯一交接](docs/项目交接文档.md)、[全项目审查](docs/维护/全项目审查-20261016.md)。
- 版本与经验：[CHANGELOG](CHANGELOG.md)、[踩坑记录](docs/踩坑记录/README.md)。

## 目录与维护

`skills/` 是两项技能的唯一维护源，`.agents/skills/` 是同内容发现镜像；`.cursor-plugin/` 引用原技能。`standards/` 保存公共及维护规则，`templates/` 保存接入与记录模板，`projects/` 只保留来源/差异索引，真实 SDK 和现场配置留在原项目。`docs/` 分使用、维护及验收资料，`examples/` 是有适用边界的演示。

修改后同步相关镜像与规则副本，在仓库根运行：

```powershell
python -X utf8 scripts/validate_offline.py
python -X utf8 scripts/test_sync.py
python -X utf8 -m unittest discover -s scripts -p 'test_*.py'
```

安装入口变更还需用当前候选 ZIP 运行 `scripts/test_launcher_windows.py --archive "候选ZIP路径"`，仅用临时用户根测试。日常构建 `python -X utf8 scripts/build_package.py` 输出到忽略的 `dist/candidate/`，附渠道、提交、未提交状态和内容指纹。根目录离线 JSON 是最近工具检查记录，不是业务测试结果。

成员提交 PR，由维护者审核；维护者本人或明确授权代提交按既有规则处理。main 推送只做校验，正式发布由维护者另行手动触发、递增版本并验证双平台，不覆盖旧资产。源码合并、正式发布、客户端加载分别记录。
