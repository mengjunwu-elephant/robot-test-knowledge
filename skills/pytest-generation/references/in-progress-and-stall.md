# 堵转与进行中场景

用例标题、测试目的、前置条件或测试步骤出现下列意思时，先按本节生成弹窗和接口调用，再调用本条测试接口。弹窗使用项目已有的人工确认函数。Marsdog-Head-Test 使用 `prompt_continue`：点确定继续，点取消跳过该条；5 分钟内未处理也跳过该条。真实接口调用之后写日志。不要另做连接，不要把鼻子停工况写进眼部用例。

进入该状态的命令和参数以该条官方前置或步骤里写明的调用为准。原文没有命令或参数时标待确认，不另编姿态、通道或模式。其他项目不复制 Marsdog 眼部的通道和模式。

## 堵转

出现「堵转」或相同意思时走本节。同时出现「校准中」等进行中表述时仍走堵转，不再额外插入进行中流程。

1. 弹窗：「请准备好人工介入制造堵转现象，完成后点确定。」
2. 点确定后，调用该条官方前置里用来制造堵转的那条接口，并在调用后写日志。
3. 弹窗：「请确认当前处于堵转状态，确认后点确定再调用测试接口。」
4. 点确定后，调用本条测试接口。

Marsdog 眼部已确认的制造堵转调用：

- `set_eyeball_ctrl`：`set_eyeball_ctrl(5, -20)`
- `set_blink_ctrl`：`set_blink_ctrl(50, 50, True)`
- `set_eye_gaze_ex`：`set_eye_gaze_ex(Eye.BOTH, 0, 10, 30)`
- `set_eyelid_ctrl`：`set_eyelid_ctrl(Eye.BOTH, 50, 40)`
- `set_eye_blink_ex`：`set_eye_blink_ex(Eye.BOTH, 0, 70, 0)`
- `set_eye_calibration`：`set_eye_calibration(EyeChannel.ALL, EyeCalibrationMode.POSITION)`

## 运动中、运行中、校准中、回零过程中

出现「运动中」「运行中」「校准中」「校准时」「校准过程」「校准过程中」「校准进行」「运行过程中」「回零过程中」「回零中」「回零时」或相同意思时走本节。

1. 弹窗：「本条需要设备处于{状态}。点确定后调用进入该状态的接口，返回后立即调用测试接口。」状态使用该条用例里的原词。
2. 点确定后，调用进入该状态的接口，并在调用后写日志。
3. 该调用返回后立即调用本条测试接口。中间不再弹窗，也不再插入等待，避免运动、校准或回零在测试接口发出前结束。用例自己的步骤等待仍保留在测试接口之后。

Marsdog 眼部已确认的进入状态调用：

- 校准中、校准时、校准过程、校准过程中、校准进行：`set_eye_calibration(EyeChannel.ALL, EyeCalibrationMode.POSITION)`
- 回零过程中、回零中、回零时：`set_eye_calibration(EyeChannel.ALL, EyeCalibrationMode.HOME)`
- 运动中、运行中、运行过程中：使用该条官方前置写明的运动接口和参数。原文没有参数时标待确认。
