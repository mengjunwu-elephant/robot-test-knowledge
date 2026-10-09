# Tuya_pytest 项目独立知识

观察日期：2026-10-09。

testcases/{robot,upper_body,chassis,head}，test_data 四模块工作簿。根 session device 分发子系统 Fixtures，head/conftest 独立 TCP 为例外；upper_body 自动前置上电不可复制到其他模块。保留单行 title 参数化 ID 与纯数字 Excel ID；expect_data 为业务数据，按项目 device.result_data 契约处理。运动需另行确认，状态恢复及中文 Allure 依当前 AGENTS。已有技能示例含英文 Allure 标题，与 AGENTS 的中文要求冲突，应遵守当前规则，不直接复制旧示例。

证据见 ../source-manifest.json。当前为抽样规则与源码核对，不是所有接口契约审计。原项目未修改。独立知识正式更新应在原项目 docs/knowledge 维护，公共库只维护引用索引。
