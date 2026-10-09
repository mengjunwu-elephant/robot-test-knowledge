# elephant-pytest 项目独立知识

观察日期：2026-10-09。

按产品线组织 testcases/。根 conftest 管理全局 CLI；产品目录管理 device 生命周期，附件示例为 module scope。common1/test_data_handler.py 读取 Excel。settings 的各 Base 与数据路径需按目标产品重新核对。arm_registry.py/arms.json 仅属于本项目。保留 title 参数化 ID、单行装饰器与文件日志风格；异常类从本地 SDK 核对，接口恢复不移入公共 session。

证据见 ../source-manifest.json。当前为抽样规则与源码核对，不是所有接口契约审计。原项目未修改。独立知识正式更新应在原项目 docs/knowledge 维护，公共库只维护引用索引。
