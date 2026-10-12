"""Generated from the explicitly fictional contract.json, not a robot API."""
import json
import allure
import pytest

@allure.feature("模拟配置")
@allure.title("查询当前模式")
@pytest.mark.parametrize("case", [{"id": "SIM-01", "expected": "idle"}], ids=lambda case: case["id"])
def test_get_mode(memory_device, case):
    actual = memory_device.get_mode()
    allure.attach(json.dumps({"expected": case["expected"], "actual": actual}), "预期与实际", allure.attachment_type.JSON)
    assert isinstance(actual, str)
    assert actual == case["expected"]
