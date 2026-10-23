---
name: marsdog-vision
description: 编写或迭代 Marsdog / 视觉感知 / 视觉直驱事件测试用例时的专用补充：1023 样板列与分区、前置模板、设计维度、可观察契约与禁止项；不替代 testcase-iteration 确认关口。
---

# Marsdog_vision（视觉直驱事件用例补充技能）

本技能是 [testcase-iteration](../testcase-iteration/SKILL.md) 的**视觉模块特化补充**，不替代公共确认关口与团队底线。对外说明名：**Marsdog_vision**；目录 / frontmatter：`marsdog-vision`。

启用本技能时：

1. 仍先读 testcase-iteration 的[团队公共规则](../testcase-iteration/references/team-rules.md)、[确认流程](../testcase-iteration/references/confirmation-flow.md)、[可直接操作写法](../testcase-iteration/references/practical-writing.md)。
2. 再读本目录 [前置操作](references/preconditions.md)、[设计维度](references/design-dimensions.md)、[观察契约](references/observation-contract.md)。
3. 关口顺序不变：**Sheet 范围 → 测试点评审 → 完整方案**；生成/修订用例须有对应授权。本技能只补视觉专用前置、维度、观察对象与禁止项，**不**替代三道确认关口。  
   （Marsdog_vision 现行正文以 1023 Sheet10 采用表为源文件时，「生成八列底稿副本」**不是**默认主路径；见项目 `execution-plan`。）

合并进仓库后，上述相对链接指向包内 `skills/testcase-iteration/`；本草稿树内若无该目录，以已安装技能包为准。

## 何时启用

满足任一条件即启用本技能（可与 testcase-iteration 同轮使用）：

- 产品/模块为 **Marsdog**、**视觉感知**、**视觉直驱事件**（含身份入画、姿态/表情直驱、玩具入画等）。
- 任务是编写、迭代或审查上述范围的 Excel/CSV 用例，或从 L2/L3/直驱需求表收敛测试点。
- 用户要求按「视觉直驱」/ **1023 Sheet10 样板**（`MD-VDE-*`、模块 A～G）写法产出。

非视觉直驱（纯夹爪 SDK、纯固件协议、与视觉无关的 ROS Service 等）不要加载本技能全文。

## 与 testcase-iteration 的关系

| 层 | 谁负责 |
| --- | --- |
| 三道确认关口、模板保真、格式检查、生成授权 | **testcase-iteration**（不可跳过） |
| 1023 Sheet10 样板列/分区、视觉调试前置、事件名已确认 vs 待确认、情绪可测 vs 观测待确认、扩展须批准、观察契约与禁止项 | **本技能（Marsdog_vision）** |
| 未授权连真机 / 不猜填阈值 / 示例不当契约 | 两边共同遵守；视觉场景以本技能禁止节为准加严 |

不得用本技能绕过 Sheet / 测试点 / 方案确认。已有相同范围授权时，不重复索要相同批准，但视觉专用缺口仍须标「待确认」。

## 样板列 / 分区 / 编号（对齐 1023 Sheet10）

权威写法样本在**业务 / Project 侧**采用表，**不要**把完整业务 CSV 拷进本技能包。列与风格对齐：

| 项 | 口径 |
| --- | --- |
| 编号 | `MD-VDE-{A～G}{序号}`（如 `MD-VDE-A01`） |
| 所属模块 | **A** 身份 · **B** 情绪 · **C** 姿态/物品 · **D** 时序/多目标 · **E** 仲裁 · **F** 性能 · **G** 稳定 |
| 主列 | 用例编号 / 功能名称 / 所属模块 / 测试目的 / 优先级 / 前置条件 / 测试步骤 / 预期结果 + 备注 + 环境实测块 |
| 公共前置 | `ros2 launch marsdog_vision_interaction vision_debug.launch.py web_host:=0.0.0.0` · `http://<IP>:8765` · `ros2 topic echo /perception/visual_event` |

若用户书面指定改回旧功能表八列，以当次 Sheet 关口为准，并在方案写明；**默认按 1023 Sheet10 多列样板**。

## 事件名策略（草稿 vs 已确认）

| 状态 | 预期列 | 备注列 |
| --- | --- | --- |
| **已开发确认** | 可写入约定名（如 `EVT_VISION_*`）并作成立断言 | 可注明确认来源（开发/L2 拍板） |
| **未确认** | 写 **「待确认」**（可带 ENTER/HOLD/EXIT/TRIGGER） | 可追溯草稿名，标明非正式 |
| **仅 L2/L3/外部草稿** | **禁止**冒充正式名写入预期 | `草稿：EVT_…（非正式）` |

编写时须在方案或备注中**区分**「表内已按开发确认硬写」与「仍待确认」；禁止把外部样本一律升格为已拍板契约，也禁止在已确认条目上强行改回「一律待确认」而与采用正文打架（除非用户改口）。

## 情绪口径

| 原则 | 写法 |
| --- | --- |
| 采用表中的**硬测项** | 按**可测**写 L2 增量/表现/双分支等 |
| **观测手段未定** | 标 **待确认**；可写意图，通过判定须注明依赖（调试页/API 等） |
| 产品确认「不验收情绪」的场景（如表内弯腰） | 遵从产品口径，不硬断言 Δ |
| **禁止** | 假装「本轮情绪一律挂起」而与 1023 Sheet10 硬测正文矛盾；也禁止无观测却勾选情绪已通过 |

主抓仍是画面成立 → `/perception/visual_event` 上报与一次直驱；情绪与事件可同条（1023 Sheet10 常见），不强制拆行挂起。

## 默认生成范围 vs 扩展分区

| 范围 | 态度 |
| --- | --- |
| **默认** | 经典直驱**主路径**：8 画面事件 + 对应状态机/重触发/时序门控 + 与之重叠的可测情绪 |
| **扩展（须书面批准范围才生成）** | Stop / 跌倒 / 仲裁整组 / 狗粮(FOOD) / 中性 / 大幅负向姿态 / 门控新需求等 A07+/C03+ / E 区等 |
| **待补洞**（有方案清单时） | 低置信专条、玩具准确率、节点重启、崩溃拉起等 — 不假装已覆盖 |

未获书面批准时，**不要**因样本或外部稿出现扩展条就扩进本轮阻塞交付。

## 必读参考（本技能）

- [前置操作模板](references/preconditions.md)
- [用例设计维度](references/design-dimensions.md)
- [观察契约与禁止断言](references/observation-contract.md)
- [样例说明](examples/README.md) — 指向 Project/业务侧 1023 Sheet10 路径；不内嵌完整工作簿

## 简要流程（视觉轮次）

1. **Sheet / 正文形态**：确认采用 1023 Sheet10 样板或多列修订；扩展模块是否批准。  
2. **测试点**：经典主路径 + 已批准扩展；标待确认依据与待补洞。  
3. **方案**：事件名已确认/待确认表、情绪可测/待确认、P 级与生成范围；取得生成/修订授权。  
4. **落笔**：前置用本技能模板；预期遵守事件名与观察契约；扩展未批准不落阻塞行。  
5. **交付检查**：testcase-iteration 结构/格式 + 本技能语义自检（见 observation-contract）。

## 禁止（摘要）

完整列表见 [observation-contract.md](references/observation-contract.md)。硬禁止包括：猜填未证实阈值；未批准扩 L3/扩展画面为阻塞项；把示例/未确认 `EVT_*` 当契约；已确认与草稿不分；伪造「情绪一律挂起」；未授权连真机；完整业务工作簿进 skills。
