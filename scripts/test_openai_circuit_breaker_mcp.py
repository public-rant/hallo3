import openai_circuit_breaker_mcp as mcp

def test_check_recent_costs_true(monkeypatch):
    # Simulate nonzero costs for today/yesterday
    monkeypatch.setattr(mcp, "fetch_usage", lambda date: 123)
    assert mcp.check_recent_costs() is True

def test_check_recent_costs_false(monkeypatch):
    # Simulate zero cost both days
    monkeypatch.setattr(mcp, "fetch_usage", lambda date: 0)
    assert mcp.check_recent_costs() is False

def test_check_recent_costs_partial(monkeypatch):
    # Simulate cost today, none yesterday (calls twice)
    results = [100, 0]
    monkeypatch.setattr(mcp, "fetch_usage", lambda date: results.pop(0))
    assert mcp.check_recent_costs() is True

def test_check_recent_costs_api_error(monkeypatch):
    # Simulate API error (function throws)
    def fetch_usage_raises(date):
        raise Exception("Test API error")
    monkeypatch.setattr(mcp, "fetch_usage", fetch_usage_raises)
    # Should handle error and return False (cost = 0)
    assert mcp.check_recent_costs() is False
