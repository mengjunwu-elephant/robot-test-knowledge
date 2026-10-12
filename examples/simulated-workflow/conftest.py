"""Isolated memory-only fixture; no device/project imports."""
import pytest

class MemoryConfig:
    def __init__(self):
        self.mode = "idle"
        self.calls = []
    def get_mode(self):
        self.calls.append(("get_mode",))
        return self.mode
    def set_mode(self, mode):
        self.calls.append(("set_mode", mode))
        if mode not in ("idle", "eco"):
            raise ValueError("unsupported mode")
        self.mode = mode
        return {"accepted": True}

@pytest.fixture(scope="function")
def memory_device():
    return MemoryConfig()

class MemoryService:
    def __init__(self):
        self.mode = "idle"
        self.requests = []
    def call(self, service, request, timeout_s):
        assert timeout_s == 0.5, "timeout must use the fictional contract"
        self.requests.append((service, dict(request), timeout_s))
        if service == "get_mode":
            assert request == {}
            return {"success": True, "data": self.mode}
        assert service == "set_mode"
        assert set(request) == {"mode"}, "validation controls leaked into request"
        if request["mode"] not in ("idle", "eco"):
            return {"success": False, "error": "MODE_INVALID"}
        self.mode = request["mode"]
        return {"success": True, "data": "ok"}

@pytest.fixture(scope="function")
def memory_service():
    return MemoryService()
