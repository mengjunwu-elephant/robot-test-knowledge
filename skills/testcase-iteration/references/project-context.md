## elephant-pytest
按产品线组织 testcases/。根 conftest 管理全局 CLI；产品目录管理 device 生命周期，附件示例为 module scope。common1/test_data_handler.py 读取 Excel。settings 的各 Base 与数据路径需按目标产品重新核对。arm_registry.py/arms.json 仅属于本项目。保留 title 参数化 ID、单行装饰器与文件日志风格；异常类从本地 SDK 核对，接口恢复不移入公共 session。

## Tuya_pytest
testcases/{robot,upper_body,chassis,head}，test_data 四模块工作簿。根 session device 分发子系统 Fixtures，head/conftest 独立 TCP 为例外；upper_body 自动前置上电不可复制到其他模块。保留单行 title 参数化 ID 与纯数字 Excel ID；expect_data 为业务数据，按项目 device.result_data 契约处理。运动需另行确认，状态恢复及中文 Allure 依当前 AGENTS。已有技能示例含英文 Allure 标题，与 AGENTS 的中文要求冲突，应遵守当前规则，不直接复制旧示例。

## Tuya_Ros2
五模块 environment/upper_body/chassis/head/perception，原始 test_data/source 只读。运行表含 ID、automation_id、title、api、ros_kind、endpoint、ros_type、parameters、expect_data、test_type。fixture robot_ros2 为 session，ROS/SSH 生命周期不可套用 SDK device。代表性代码以 automation_id 参数化，保留该差异；JSON 用 json.loads。资料和规则要求全局唯一 automation_id、一接口一 Sheet/文件。禁止 collection 建立远程或 ROS 连接。当前 API 与 endpoint 必须重新核对，不能从 SDK 项目搬用。
