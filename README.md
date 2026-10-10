# 大象机器人软件测试知识库

这是测试团队共同维护的测试规范、项目经验和 Codex Skills 仓库。测试人员提供项目资料，在对话中调用技能，辅助完成用例编写、用例审查和单接口 pytest 代码生成。

**当前待发布版本：0.5.0（最近正式版0.4.1）。** 本页更新日期：2026-10-10。版本信息以 [plugin.json](plugin.json) 和 [正式发布页](https://github.com/mengjunwu-elephant/robot-test-knowledge/releases/latest) 为准。

第一次使用，先读第 3、4 节；编写用例看第 5、6 节；维护或发布看第 9、11 节。只使用技能的测试人员不需要先学会仓库全部脚本。

### Cursor：从 GitHub 直接安装

仓库已提供 Cursor 导入清单，复用同一份两项技能。支持该功能的 Cursor 中：

1. 打开 **Customize（自定义）**，选择 **From GitHub Repository（从 GitHub 仓库导入）**。
2. 粘贴 `https://github.com/mengjunwu-elephant/robot-test-knowledge`。
3. 导入后找到 `robot-test-knowledge`（大象机器人测试技能包），点击 **Install**。
4. 开启新对话，输入 `/`，选择 `testcase-iteration` 或 `pytest-generation`。
5. 例如：选择用例技能后说“审查本项目已有 Excel，先读取项目规则和接口资料，列出缺口，不连接实体机器人”。

如果看不到 GitHub 导入入口，先核对 Cursor 版本是否支持插件；也可以将两个完整技能文件夹放入本机 `~/.cursor/skills/`。不要同时安装同名的手动副本和插件，以免版本混淆。

**更新与版本**：Cursor 通过导入来源刷新、更新插件；本仓库的 `Install.cmd`、`Update.cmd` 仅服务 Codex/Work。技能内提到 `Update.cmd` 时，在 Cursor 应改用其插件更新入口。GitHub 导入通常使用来源所跟踪的分支，不能把它说成自动只跟随 GitHub Release；团队如启用 Auto Refresh，需核对跟踪分支和 GitHub App 权限。当前未验证用户 Cursor 的实际安装、自动刷新或正式版锁定。

维护者修改技能版本时，需同步根 `plugin.json` 与 `.cursor-plugin/plugin.json`；离线校验会检查二者一致。既有 v0.4.1 ZIP 保持原样，Cursor 从仓库导入新清单。

格式与入口依据：[Cursor 插件参考](https://cursor.com/docs/reference/plugins)、[Cursor 技能说明](https://cursor.com/docs/skills)。此入口不代表已上架 Cursor 官方市场；团队市场需要相应团队套餐和权限。

## 1. 知识库解决什么问题

不同项目中，经常重复处理类似的问题：资料是否完整、用例字段怎么填、测试目的是否清楚、边界值有没有依据、旧版本用例怎样迁移、生成的 pytest 是否符合原项目框架。

本仓库采用“公共知识 + 项目独立知识 + 共享技能”：

- **公共知识**：测试设计、版本变更、证据、结果记录和团队维护方法。
- **项目独立知识**：型号、SDK/固件版本、真实接口、Excel 加载方式、Fixtures、Allure 和恢复逻辑等差异。
- **共享技能**：将公共方法变成可以在对话中调用的工作流程，并附带适用模板和检查工具。

共享规范不能替代接口契约。例如，Python 库对非法参数抛出 `ValueError`，并不能证明设备对非法协议帧会返回某个错误码。

## 2. 当前有哪些可用能力

### 0.5.0：用例确认与格式规则

写用例分四步：**确认实际Sheet范围 → 单独评审并确认测试点 → 确认完整方案 → 生成Excel副本**。前一阶段认可后才进入下一阶段；批准技能更新不能代替批准项目用例范围。

采用夹爪v1.4.1格式基线时，正文微软雅黑10号、垂直居中、自动换行、黑色细线全边框。编号、功能名称、测试接口、优先级居中；目的、前置、步骤、预期、执行记录和备注等按配方左对齐；表头10号加粗居中，封面单独保留布局。完整规则见[格式规则](skills/testcase-iteration/references/cell-format.md)、[三道确认关口](skills/testcase-iteration/references/confirmation-flow.md)。原表混用Carlito11号属于已发现异常，不直接沿用。

新增只读格式检查：`python skills/testcase-iteration/scripts/review_format.py --workbook "用例副本.xlsx" --sheet "串口指令测试结果" --report "格式检查.json"`。每个批准Sheet重复一个`--sheet`；结构内容仍用原review_workbook.py检查。格式静态通过不能代替视觉和语义评审。

### 用例编写与迭代：`testcase-iteration`

适用于新建、审查或迭代通用软件、固件、ROS 测试用例。可以辅助：

- 核对新旧完整版本，以及新增、修改、删除或无变更内容。
- 读取当前项目规则、模板、需求和接口资料，识别缺口与冲突。
- 设计独立测试点，写清目的、输入、步骤、预期、前置与恢复责任。
- 保留原字段、Sheet、编号、环境记录、公式、格式和历史证据。
- 生成用例副本及逐项变更说明，进行部分结构和填写规则的只读检查。

包内附带三份 V1.0 模板：通用软件、固件、ROS。模板“填写说明与示例”页中的结果是演示数据，不能作为真实执行记录或计入正式统计。

### pytest 生成：`pytest-generation`

适用于依据**已确认用例**新增或修改单接口 pytest 测试。先读取当前源码、Excel 加载器、Fixtures 和邻近测试，再按照原项目方式生成代码，保护 Allure、参数化 ID、marker、skip、单接口结构与恢复逻辑。

资料不足时列出待确认项，不臆造接口、限位、异常或预期。生成代码需要审查和适当验证，不是脱离项目资料的一键自动测试程序。

### 尚未实现

- `defect-analysis`：失败日志、复现与根因分析。
- `coverage-review`：接口、用例和代码覆盖核对。
- `test-report`：依据真实 pytest/Allure 结果整理报告。

这三项目前只有 [扩展规划](skills/ROADMAP.md)，不能作为独立技能调用。本仓库不包含完整 SDK 契约，不自动连接、控制或测试实体机器人，也不自动读取或上传所有项目。

## 3. 怎样下载安装

### 使用前准备

1. 使用支持本地插件来源的 Codex/Work 桌面客户端。
2. 安装 Python 3.10 或更高版本。Windows 安装入口先尝试 `py`，没有时使用 `python`。
3. 准备目标项目目录与可信资料。安装插件不会把项目资料自动复制进知识库。

本包通过 GitHub 分发，未上架公共插件商店。普通网页对话无法直接读取本机插件文件。

### Windows 安装步骤

1. 打开 [最新正式版下载页](https://github.com/mengjunwu-elephant/robot-test-knowledge/releases/latest)。
2. 在 Assets 中下载 `robot-test-knowledge-0.5.0.zip`，或以后新版本同名格式的 ZIP。**不要把 GitHub 的 Source code ZIP 当作安装包。**
3. 完整解压，在解压后的 `robot-test-knowledge` 文件夹里找到 `Install.cmd`。不要在压缩包内运行，也不要只取出一个文件。
4. 双击 `Install.cmd`，查看窗口结果；窗口会保留信息供检查。
5. 完全退出并重新打开桌面客户端。
6. 打开插件目录，选择个人来源，找到“大象机器人测试技能包”，安装或启用。
7. 打开目标项目，新建对话，在技能选择器确认能找到“用例编写与迭代”和“pytest 生成”。

个人来源名称沿用电脑已有的来源名称，可能显示为“个人技能包”或其他名称，不一定与仓库同名。来源登记与应用安装是两个步骤。[官方本地插件说明](https://developers.openai.com/plugins/build/plugins)

### 安装会改动哪些文件

安装器将插件来源复制到当前用户目录的 `.codex/plugins/local/robot-test-knowledge/<版本号>/`，并登记 `.agents/plugins/marketplace.json`。应用负责管理安装后的缓存副本。

它保留其他插件条目，首次修改已有来源登记文件时保留备份；不会修改原测试项目、Excel、Fixtures 或 `config.toml`。同名外部插件冲突，或同版本文件已经被修改时，安装会停止，不直接覆盖。

其他系统可在解压后的安装包目录执行 `python3 install.py --apply` 完成登记，之后仍需在支持本地来源的客户端完成安装。已有 Windows/Linux 安装逻辑隔离测试；尚未完成 macOS 客户端实际验收。

## 4. 第一次在对话中怎么使用

**先在技能选择器选中技能，再输入任务。** 只有写出技能名字，并不证明它已经安装或加载。

支持相应入口的 Work 使用 `@` 选择，Codex 使用 `$` 引用，例如 `$testcase-iteration`、`$pytest-generation`；具体以客户端显示的选择器为准。[官方调用示例](https://developers.openai.com/plugins/build/plugins)

尽量提供以下信息：

1. 项目、产品或型号。
2. 软件/固件/SDK 新旧完整版本、本次变化；没有变化也说明。
3. 用例文件、目标 Sheet、可信接口或需求资料。
4. 本次是审查、新建还是修改，范围与输出位置。
5. 预期依据、执行环境，以及本轮只离线工作等边界。

### 示例一：先审查，不修改

选择“用例编写与迭代”，提供文件，然后输入：

> 请审查这份夹爪固件用例。版本为 v1.4.1，本次功能和协议没有变化。以我提供的协议和指定 Python 库为依据，逐条核对测试目的、步骤、预期和模板字段。指出库校验与固件响应的差异；有资料冲突时列出来源和影响，让我选择。先只审查，不改原件，不连接设备。

### 示例二：确认后生成副本

> 确认执行。按刚才确认的范围修订用例副本，保留原 Sheet、编号、环境表头和历史记录。新版本的实际结果保持空白，交付逐项变更说明和检查结果，更新项目已有方案总文档与唯一交接文档。

新方案先通过至少三个问题收敛版本、范围、依据和交付边界，收到“确认执行”后实施；已确认任务范围内不反复询问相同问题。

### 示例三：生成单接口 pytest

选择“pytest 生成”，然后输入：

> 检查 elephant-pytest 的 mycobot_450/get_debug_state。读取当前项目规则、对应 Excel Sheet、Fixtures 和邻近测试；依据已确认用例生成单接口测试副本，保留原 Allure 和参数化方式。不连接机器人，不执行原项目 collection；资料不足的预期先列为待确认。

将示例中的项目、接口和版本替换成实际目标。技能需要重新核对当前文件，不能只凭知识库历史快照生成。

## 5. 三类用例怎么编写

### 通用软件

拆出可独立判断的功能行为，再按风险选择正常、边界、异常、状态转换、兼容和恢复场景。目的写“什么场景、验证什么目标”，步骤写具体操作与输入，预期写可观察、可判定的结果。

使用通用软件模板中的功能模块和适用专项 Sheet，保留编号、功能名称、目的、优先级、前置、步骤、预期及每个环境的四列记录。[具体写法](skills/testcase-iteration/references/general-software.md)

### 固件与协议

核对协议、参数编码、单位、版本和真实接口。接口表保留“指令序号”“测试接口”等专用字段；响应时间与老化测试使用各自原字段，不套入简化通用表。

使用 Python 库时核对真实方法、输入范围和返回行为。库缺少的方法、设备错误码、时间阈值或恢复方式缺乏依据时，保留待确认，不凭示例补齐。[具体写法](skills/testcase-iteration/references/firmware.md)

### ROS

分别核对 Service、Topic、Action 的名称、类型、字段、版本和运行条件。Service 检查请求响应与恢复；Topic 检查消息、采样和反馈关联；Action 检查目标、反馈、结果、取消与超时。

发布成功不能证明设备动作完成。人工模板也不能直接替换成自动化加载器字段。[具体写法](skills/testcase-iteration/references/ros.md)

### 共同要求

- 新表从适用模板副本开始；旧表不因技能升级而被强制改结构。
- 每个独立测试项分别写目的与判定结果，不跨项合并步骤、预期或结果。
- 使用 P0—P3 优先级，不能把它当成缺陷严重程度。
- 每个环境分别记录实际结果、执行状态、回归测试记录和测试证据。
- 未执行不得写 Pass；旧版结果不能迁成新版本结论。
- 参数、阈值、异常和预期需要可信依据；明确部分继续，缺口保留待确认。

## 6. 资料或规则冲突怎么办

团队测试规范范围内，**默认采用技能包规则，同时提示冲突，让使用者选择**。用户当次明确选择后记录来源和版本，再执行受影响修改；用户指令与平台约束优先。

提示应写清冲突位置、双方来源与版本、不同处理的影响和默认选择。例如旧资料写“非法参数返回 FF”，库先抛 `ValueError`，应区分库层用例与原始协议用例，不能把它们当成同一结果。

涉及接口签名、返回值、单位、限位或验收阈值的冲突，公共规范不能证明哪份契约正确。此时标记待确认，继续其他有依据的部分。[冲突处理说明](skills/testcase-iteration/references/conflicts.md)

## 7. 如何检查用例副本

在对话里补充：“请对副本做只读检查，输出问题所在 Sheet 和单元格，同时列出人工仍需核对的内容。”

包内工具使用 Python 标准库，不需要联网安装依赖。可检查表头字段与位置、两层表头合并、必填项、优先级、同表编号、状态、部分结果与证据规则，以及跨独立项合并问题。

**检查通过不等于测试通过。** 工具不验证接口预期是否正确，不重算公式，也不检查全部样式、视觉表现或设备行为。环境首页、颜色、边框、语义和正式验收仍需人工核对。

维护者需要手动运行时，在仓库根目录执行并替换为真实路径：

```powershell
python -X utf8 skills/testcase-iteration/scripts/review_workbook.py --workbook "用例副本.xlsx" --category firmware --report "检查结果.json"
```

- 类别：`general` 通用软件，`firmware` 固件，`ros` ROS。
- 默认设计阶段要求执行记录为空；检查已有历史结果时加 `--mode executed`，不要为了通过检查清空历史。
- `--allow-empty` 仅用于检查空模板，不代表完成用例设计。
- Sheet 改名时加 `--mapping "映射.json"`，例如文件内容为 `{"串口指令测试结果":"功能模块（接口测试）"}`。
- 未映射 Sheet、待确认内容与未重算公式会提示未解决项。返回码 0 表示本轮静态检查未发现问题，1 表示发现问题或未解决项，2 表示读取或参数检查无法完成。

工具不保存或清洗工作簿，示例说明页不计入正式用例。在解压的安装包内运行时，从 `skills/testcase-iteration` 目录使用 `python scripts/review_workbook.py ...`。[完整工具说明](skills/testcase-iteration/references/workbook-review.md)

## 8. 更新、回退和卸载

“跟随最新版”指使用维护者发布的**最新正式 Release**，不是所有 `main` 提交、草稿或预发布版本。

### 推荐更新方式

1. 查看 [最新正式版](https://github.com/mengjunwu-elephant/robot-test-knowledge/releases/latest) 与 [变更日志](CHANGELOG.md)。
2. 下载并完整解压新包，运行新包 `Install.cmd`。
3. 刷新来源、更新或重新安装插件，重启客户端并开启新对话。
4. 确认技能报告的版本，再开始任务。

也可以运行解压目录的 `Update.cmd`，它尝试下载最新正式版并核对发布校验值后登记。遇 GitHub API 403 限流或网络错误时保留原安装，改用手动下载。

目前没有定时自动更新，也没有正在进行的对话热更新。更新逻辑的隔离测试已通过，真实匿名请求曾遇到限流，尚不能宣称所有环境的在线更新已完成验收。

### 回退与卸载

需要回退时，从 Releases 下载指定旧正式版，运行该版本安装器，再刷新插件并开启新对话。旧版本保留，但回退后仍需核对项目资料与规则差异；回退流程尚未完成完整客户端验收。

卸载在应用插件目录操作。来源登记和本地版本文件不会自动删除。不要直接修改缓存，再要求安装器覆盖被修改的同版本文件。

## 9. 跨项目使用与默认规则接入

安装到个人来源后，可在不同项目主动调用技能；**安装技能不会自动把它变成所有项目每次对话都读取的规则**。

希望项目默认提醒使用团队规范时，将 [项目接入片段](templates/项目接入-AGENTS片段.md) 合并进该项目已有 `AGENTS.md`，保留原内容，不整文件覆盖；没有该文件时再建立适用入口。

项目规则继续保留型号、接口、框架和环境差异。安装包不自动改项目规则；三个来源项目目前未被批量接入。接入片段提供的是使用入口，不能保证客户端无条件加载技能。

## 10. 团队共同维护和发布

### 普通测试人员

1. 从 `main` 创建修改分支。
2. 修改相关规则、技能或模板，说明真实问题、依据、前后行为及影响项目。
3. 修改 `skills/` 后同步对应 `.agents/skills/` 文件；公共规则变更同步两个技能的 `references/team-rules.md`。
4. 做与修改相关的检查，更新变更日志和唯一交接文档。
5. 提交 PR，由 @mengjunwu-elephant 审核合并。

反馈建议附：使用版本、项目/接口、任务描述、实际输出、期望行为、相关文件或问题单元格，以及判断依据。敏感信息先去除。

### 仓库所有者

**@mengjunwu-elephant 本人提交，或明确授权代为提交的修改，免人工审批，可直接提交或合并。** 其他测试人员继续审核。免人工审批不等于免除必要校验。

目前普通成员受 PR、维护者审核及双平台检查保护，管理员不强制受相同审批限制。[完整协作约定](CONTRIBUTING.md)

### 长期维护修改哪里

- 技能工作方式：`skills/<技能名>/SKILL.md` 和相关 references、scripts、assets。
- 公共规范：`standards/` 以及随技能分发的公共规则。
- 项目差异与来源快照：`projects/`，不能代替当前源码或接口资料。
- 安装入口：`packaging/`；构建与测试：`scripts/`。
- 不将个人安装目录或缓存作为长期维护源，不单独修改 `.agents/skills/` 镜像。

### 发布步骤

1. 修改技能包内容时提高 `plugin.json` 版本，更新 `CHANGELOG.md`，不复用已发布版本号替换不同内容。
2. 将通过校验的修改合并到 `main`。
3. @mengjunwu-elephant 在 GitHub Actions 打开 **Build robot test skill package**，选择 `main`，点击 **Run workflow**。
4. Windows/Linux 校验通过后才发布正式 ZIP 和 `SHA256SUMS.txt`；当前工作流仅允许该维护者触发发布。
5. 成员从正式版安装，再按当前项目资料试用。

普通推送不自动发布。仅修改 README 等不进入安装包的说明，通常不必升级技能包版本或重新发布原 Release。

## 11. 仓库目录怎么看

```text
robot-test-knowledge/
├── README.md                 使用入口
├── AGENTS.md                 本仓库规则
├── CONTRIBUTING.md           协作、本人免审和发布要求
├── CHANGELOG.md              版本变化
├── plugin.json               插件身份与版本
├── standards/                公共规范与同步方式
├── fundamentals/             证据与测试设计原则
├── skills/                   两项技能唯一维护源
│   ├── testcase-iteration/
│   │   ├── SKILL.md          用例编写与迭代入口
│   │   ├── references/       三类写法、冲突、示例与来源
│   │   ├── assets/templates/ 三类原样模板
│   │   └── scripts/          工作簿只读检查
│   └── pytest-generation/    单接口pytest生成
├── .agents/skills/           本仓库发现副本
├── .agents/plugins/          仓库插件来源目录
├── projects/                 来源快照与项目差异
├── templates/                接入、契约、变更与审查模板
├── packaging/                安装、更新入口与说明
├── scripts/                  构建、检查与隔离测试
├── .github/                  PR、审核归属与工作流
└── docs/                     详细说明、方案总文档与唯一交接
```

安装 ZIP 不是完整仓库，仅含安装/更新入口、插件定义、技能及其资源。三类模板与相关规范条款可随包使用；现场业务工作簿、原项目源码、原始会话、密钥和连接配置不会自动打包。

## 12. 维护者离线检查

在仓库根目录，用 Python3.10+ 执行本次修改适用的检查：

```powershell
python -X utf8 scripts/validate_offline.py
python -X utf8 scripts/test_case_review.py
python -X utf8 scripts/test_sync.py
python -X utf8 scripts/test_package.py
python -X utf8 scripts/test_update.py
python -X utf8 scripts/build_package.py
```

第一个脚本检查目录、语法、技能格式、引用和镜像；后续分别检查工作簿规则、固定提交同步、安装和更新行为。构建输出在 `dist/`。

Windows 安装入口变更后运行 `python -X utf8 scripts/test_launcher_windows.py`，它生成包含 ZIP 的自解压 CMD，并在临时用户目录验证成功/失败路径，不写真实个人安装目录。

`python -X utf8 scripts/validate_offline.py --sources` 仅适用于能访问 `projects/source-manifest.json` 所列来源路径的电脑，只读比较原文件哈希。其他成员缺少这些路径时，来源失败不等于技能结构失败，应维护自己的来源索引。

高级固定提交导出见 [Git同步说明](standards/git-sync.md)，与个人插件更新是两种方式；默认预览，应用时拒绝覆盖同名技能和已有 lock，不是自动升级器。

## 13. 常见问题

### 双击安装失败

确认已完整解压、`Install.cmd` 与 `install.py` 同目录，且 `py` 或 `python` 能找到 Python3.10+。在命令窗口运行入口以保留错误。

独立自解压 CMD 的日志在同文件旁的 `.log` 中；普通 ZIP 内 `Install.cmd` 主要在窗口显示结果，不承诺单独日志。反馈时带上错误文本，不发送密码或连接配置。

### 安装完成却找不到技能

来源登记不等于应用已安装。重启客户端，选择个人来源，安装/启用插件，再开新对话；检查是否被项目设置禁用，以及客户端是否支持本地来源。

### 改了代码却仍使用旧规则

仓库源码与已安装副本不同。维护者发布新版本后，使用者更新并刷新插件，再开新对话。仅拉取仓库或继续旧对话，不等于更新安装。

### 字段不匹配或 Sheet 未映射

先比较当前表与所选模板，确认版本和用户选择。模块 Sheet 改名时提供映射；确有独立结构时人工评审并维护适用映射，不能为检查通过而擅自改原字段。

### 静态检查通过能否填 Pass

不能。实际结果只能来自真实执行；接口预期、业务正确性、完整样式和设备行为仍需相应验收。

## 14. 当前验证状态与后续完善

0.4.1 已完成 Windows/Linux 发布校验；安装和更新采用临时用户目录测试，Windows 自解压入口验证了成功/失败路径。用例检查13项测试、安装7项、更新2项通过，并完成固定提交同步核对与技能结构检查。

真实夹爪用例做过只读试用，可发现既有必填和待确认缺口；不等于其业务评审或设备验证已完成。用户曾确认旧版桌面安装成功，不能据此声称所有成员已完成新版调用验收。

后续需持续补充可信接口契约、实际试用案例、资料失效检查、团队接入，以及缺陷分析、覆盖审查和报告技能。历史交接保留旧阶段信息；当前状态以本页、正式版本和交接最新记录为准。

## 15. 继续阅读

- [用例编写技能使用](docs/用例编写技能使用.md)
- [团队使用步骤](docs/团队使用步骤.md)
- [技能包安装指南](docs/技能包安装指南.md)
- [技能包迭代维护](docs/技能包迭代维护.md)
- [项目接入片段](templates/项目接入-AGENTS片段.md)
- [方案总文档](docs/方案总文档.md)
- [唯一项目交接文档](docs/项目交接文档.md)
- [变更日志](CHANGELOG.md)
- [官方插件打包和本地安装说明](https://developers.openai.com/plugins/build/plugins)
- [官方Skills概念说明](https://developers.openai.com/plugins/concepts/skills)
