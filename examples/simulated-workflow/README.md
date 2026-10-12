# 纯模拟流程验收

这里的接口、参数和返回值来自本目录明确虚构的contract.json，仅用于技能维护验收，不是机器人SDK规则，也不应复制到真实项目。工作簿cases.xlsx含查询、普通设置、异常三条有依据用例及一条明确缺契约的阻塞项。

layout.json是本次模拟批准的字段语义和顺序，保留期望在第一列、编号在第三列等项目差异。结构检查应识别四条且报告SIM-04待确认；格式按团队规则检查。内容审查逐项对照模拟契约，视觉另看实际渲染，不用静态通过替代。

自动化只为SIM-01/02/03生成，单接口文件使用已有memory_device fixture、参数化身份和Allure。SIM-04未生成，因为缺单位、范围和签名。conftest.py仅创建内存对象，无设备连接或原项目依赖。

在安装了pytest和allure-pytest的隔离Python环境中可重放模拟测试（这不是原项目测试）：

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest -c examples/simulated-workflow/pytest.ini --confcutdir=examples/simulated-workflow examples/simulated-workflow -q
```

测试插件自动加载应关闭，只启用明确需要的插件。本次执行记录、四项检查范围与局限见[模拟验收](../../docs/维护/模拟流程验收-20261012.md)。标准库工具回归不依赖pytest/Allure；模拟运行的依赖与结果单独记录。

另有三条纯内存Service测试，验证请求字段与检查控制项分离、状态与业务值分别断言、拒绝响应及恢复。没有ROS运行时、端点或Topic频率阈值。使用python examples/simulated-workflow/verify_faults.py可重放7项故障探测（需要上述pytest/Allure依赖）。
