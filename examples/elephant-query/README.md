# elephant-pytest 查询接口静态试用

仅复制现有 mycobot_450/test_9_get_debug_state.py 为演示副本，修正 Allure step 的 get_atom_version 名称为实际调用 get_debug_state；不改变函数、Excel 读取、fixture、参数化、断言和日志。源码确实存在这个标签错配。
AST 语法校验通过；未导入示例，未 collection，未调用机器人。fixture 为产品目录 module 级 device，由 build_device 创建，不能运行本例来验证离线行为。
现有类型断言接受 bool（Python bool 是 int 子类），是否需排除 bool 取决于已批准 SDK 契约，本轮不擅自修改。返回合法值范围及版本契约未核实，不新增边界/异常测试。
附属 PWM 查询示例含 setter 前置与 teardown，不能仅凭 get 名称认为其执行只读，因此未选它作本次示例。
用例迭代成果：保留现有正常数据，只记录契约缺口；pytest-generation 成果：审查并输出最小报告标签修正副本。该修正不是已应用到原项目的修改。
