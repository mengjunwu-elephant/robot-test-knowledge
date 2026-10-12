"""Fictional setters distinguish request, transport status and business data."""
import json
import allure
import pytest

@allure.title("模拟Service设置并恢复")
@pytest.mark.parametrize("case", [{"automation_id": "ROS-SIM-02", "parameters": {"mode": "eco"}, "expected_return": "ok", "expected_data": "eco", "timeout_s": 0.5}], ids=lambda case: case["automation_id"])
def test_service_set_mode(memory_service, case):
    snapshot = memory_service.call("get_mode", {}, timeout_s=case["timeout_s"])
    assert snapshot["success"] is True
    original = snapshot["data"]
    assert original in ("idle", "eco")
    primary = None
    try:
        request = {"mode": case["parameters"]["mode"]}
        response = memory_service.call("set_mode", request, timeout_s=case["timeout_s"])
        allure.attach(json.dumps({"request": request, "response": response}), "Service请求与响应", allure.attachment_type.JSON)
        assert response["success"] is True
        assert response["data"] == case["expected_return"]
        actual = memory_service.call("get_mode", {}, timeout_s=case["timeout_s"])
        assert actual["success"] is True
        assert actual["data"] == case["expected_data"]
    except Exception as error:
        primary = error
        raise
    finally:
        try:
            restored = memory_service.call("set_mode", {"mode": original}, timeout_s=case["timeout_s"])
            actual = memory_service.call("get_mode", {}, timeout_s=case["timeout_s"])
            allure.attach(json.dumps({"expected": original, "response": restored, "actual": actual}), "Service恢复证据", allure.attachment_type.JSON)
            assert restored == {"success": True, "data": "ok"}
            assert actual == {"success": True, "data": original}
        except Exception as recovery:
            if primary is not None:
                raise primary from recovery
            raise

@allure.title("模拟Service业务拒绝且状态不变")
@pytest.mark.parametrize("case", [{"automation_id": "ROS-SIM-03", "parameters": {"mode": "invalid"}, "expected_error": "MODE_INVALID", "timeout_s": 0.5}], ids=lambda case: case["automation_id"])
def test_service_rejection(memory_service, case):
    before = memory_service.call("get_mode", {}, timeout_s=case["timeout_s"])
    response = memory_service.call("set_mode", {"mode": case["parameters"]["mode"]}, timeout_s=case["timeout_s"])
    allure.attach(json.dumps(response), "实际业务拒绝", allure.attachment_type.JSON)
    assert response["success"] is False
    assert response["error"] == case["expected_error"]
    assert memory_service.call("get_mode", {}, timeout_s=case["timeout_s"]) == before
