# 批准项目字段布局

仅在真实表头已经核对、用户选择采用项目字段时使用。映射文件是检查参数，不改Excel。不要把下例当作所有项目的新模板或默认字段集合。

## 一个布局同时给两个检查工具

下例的表头在第1行，字段发生调列且使用项目别名。status/actual/evidence明确配对，所以结果列不必相邻。

```json
{
  "模拟软件": {
    "start_row": 1,
    "header_rows": 1,
    "fields": {
      "A": {"label": "期望描述", "role": "预期结果"},
      "B": {"label": "执行判定", "role": "执行状态"},
      "C": {"label": "案例号", "role": "用例编号"},
      "D": {"label": "操作记录", "role": "测试步骤"},
      "E": {"label": "观察值", "role": "实际结果"},
      "F": {"label": "凭证", "role": "测试证据"}
    },
    "required_roles": ["用例编号", "测试步骤", "预期结果"],
    "header_merges": [],
    "execution_groups": [{"status": "B", "actual": "E", "evidence": "F"}]
  }
}
```

```text
python scripts/review_workbook.py --workbook "原用例.xlsx" --category general --layout "布局.json" --mode executed --report "结构报告.json"
python scripts/review_format.py --workbook "原用例.xlsx" --baseline team --layout "布局.json" --report "格式报告.json"
```

- start_row是表头起始行，header_rows是表头最后一行的行号，两者均从1开始。上方封面/说明不在该网格检查范围。
- fields键是原列字母。字符串表示实际标签与语义相同；对象分别声明label与role。工具核对该列表头区最后一个非空标签；已知字段不能改映射成无关语义。
- required_roles必须列出本项目批准的必需字段语义。其缺失或正文为空会报错；这是明确契约，不能为了过检查删掉项目必填要求。
- header_merges必须给出批准表头合并范围，无合并填[]。多层表头的上层分组另用headers声明，比如{"D1":"环境A"}，与实际表头逐项核对。非常规多表拼接需拆清范围或人工检查，不能声称任意Excel都自动适配。
- execution_groups将每个执行状态与实际结果、可选证据列对应。多环境分别声明，禁止复用同一列。未声明分组时提示缺口，不猜左右邻列。
- 未识别字段role报告待确认；现有结构规则识别用例编号/指令序号、接口/功能等设计字段、执行结果与证据，未知自定义业务语义不会自动被验证。
- fields必须覆盖检查网格里的实际有内容列。确需只审部分列时，用excluded_columns给出列与用户批准理由，例如{"G":"本轮仅审用例设计，执行记录另审"}。排除列不能同时映射，报告保留排除理由并标部分范围。

## 结果解释

错误标签、缺必需语义、错误执行分组不能作为有效布局。原表有内容但未声明的列报告UNMAPPED_COLUMN；不能把6格检查说成9格全检查。layout不会改变字体标准，特殊样式仍需--profile批准配方。

结构检查不推断SDK契约，格式检查不证明字段业务含义选择正确。工具验证声明与原表的一致性；批准依据由任务记录保留。
