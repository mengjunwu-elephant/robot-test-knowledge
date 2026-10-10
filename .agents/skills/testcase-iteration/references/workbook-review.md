# 字段与离线检查
完整审查时另运行scripts/review_format.py --baseline team，按团队通用标准及批准项目差异检查；它补充直接字体、字号、对齐、换行、填充和合并外框静态检查，详见[cell-format.md](cell-format.md)。原review_workbook.py仍负责结构与填写内容；两者都不替代视觉、语义评审。

新表优先复制 assets/templates 适用模板；附带原件与来源哈希。填写说明与示例页包含演示结果，不能当正式执行结果，不纳入统计。读取 references/standard-extract.md 可定位正式用例条款。
已有表使用其确认字段，不因新版模板而强改。发生差异先用 conflicts.md 提示用户选择，再用独立字段映射进行检查。

## 运行检查（Python3.10+，标准库，无联网依赖）
在本技能目录执行：
`python scripts/review_workbook.py --workbook "用例副本.xlsx" --category firmware --report "检查结果.json"`
类别 general、firmware、ros。默认是设计阶段，正式执行栏必须为空；维护已有实际执行结果时用 --mode executed。模板本身没有设计用例，可加 --allow-empty 检查结构。
模块 Sheet 改名时提供 --mapping "映射.json"，文件格式为 {"工作簿Sheet名":"模板Sheet名"}，例如 {"串口指令测试结果":"功能模块（接口测试）"}。未知 Sheet 提示未映射，不能忽略后宣称全表通过。首页和说明页单独排除用例计数。
工具检查表头字段和位置、两层合并、必填、优先级、同表独立编号、状态、结果与证据，报告Sheet和单元格。纵向合并的描述由锚点继承，独立结果跨项合并报错。
脚本只读文件，不保存或清洗原件，不计算/重算公式，不判断公式正确性、接口语义、来源真实程度、全部格式或视觉表现。检查通过仅表示本轮结构/内容规则通过；环境首页、颜色/边框、语义、样式与正式验收仍需人工核对。参数/预期有待确认或未知Sheet时不能宣称完整就绪。
