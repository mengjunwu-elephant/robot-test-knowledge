"""Fictional Service response semantics, with no ROS runtime."""
import json
import allure
import pytest

@allure.title("模拟Service查询模式")
@pytest.mark.parametrize("case", [{"automation_id": "ROS-SIM-01", "expected": "idle", "timeout_s": 0.5}], ids=lambda case: case["automation_id"])
def test_service_get_mode(memory_service, case):
    response = memory_service.call("get_mode", {}, timeout_s=case["timeout_s"])
    allure.attach(json.dumps(response), "Service实际响应", allure.attachment_type.JSON)
    assert response["success"] is True
    assert response["data"] == case["expected"]
