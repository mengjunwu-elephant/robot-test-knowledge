# Tuya_Ros2 项目独立知识

观察日期：2026-10-09。

五模块 environment/upper_body/chassis/head/perception，原始 test_data/source 只读。运行表含 ID、automation_id、title、api、ros_kind、endpoint、ros_type、parameters、expect_data、test_type。fixture robot_ros2 为 session，ROS/SSH 生命周期不可套用 SDK device。代表性代码以 automation_id 参数化，保留该差异；JSON 用 json.loads。资料和规则要求全局唯一 automation_id、一接口一 Sheet/文件。禁止 collection 建立远程或 ROS 连接。当前 API 与 endpoint 必须重新核对，不能从 SDK 项目搬用。

证据见 ../source-manifest.json。当前为抽样规则与源码核对，不是所有接口契约审计。原项目未修改。独立知识正式更新应在原项目 docs/knowledge 维护，公共库只维护引用索引。
