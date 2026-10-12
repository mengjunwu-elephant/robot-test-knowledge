"""Only the in-memory simulator is exercised by these examples."""
import json
import allure
import pytest

@allure.feature("模拟配置")
@allure.title("设置模式并恢复原值")
@pytest.mark.parametrize("case", [{"id": "SIM-02", "mode": "eco", "expected_return": {"accepted": True}}], ids=lambda case: case["id"])
def test_set_mode(memory_device, case):
    original = memory_device.get_mode()
    assert original in ("idle", "eco")
    primary = None
    try:
        result = memory_device.set_mode(case["mode"])
        allure.attach(json.dumps({"mode": case["mode"], "response": result}), "设置请求与返回", allure.attachment_type.JSON)
        assert result == case["expected_return"]
        assert memory_device.get_mode() == case["mode"]
    except Exception as error:
        primary = error
        raise
    finally:
        try:
            restored = memory_device.set_mode(original)
            actual = memory_device.get_mode()
            allure.attach(json.dumps({"expected": original, "actual": actual, "response": restored}), "恢复证据", allure.attachment_type.JSON)
            assert restored == {"accepted": True}
            assert actual == original
        except Exception as recovery:
            if primary is not None:
                raise primary from recovery
            raise

@allure.feature("模拟配置")
@allure.title("非法模式被拒绝且原值不变")
@pytest.mark.parametrize("case", [{"id": "SIM-03", "mode": "invalid"}], ids=lambda case: case["id"])
def test_set_mode_invalid(memory_device, case):
    original = memory_device.get_mode()
    with pytest.raises(ValueError) as caught:
        memory_device.set_mode(case["mode"])
    allure.attach(str(caught.value), "实际异常", allure.attachment_type.TEXT)
    assert memory_device.get_mode() == original
