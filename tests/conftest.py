"""Test configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Import GoFastAPI components
from gofastapi import GoFastAPI
from gofastapi.runtime import PythonBridge, HotReloader, SubinterpreterManager
from gofastapi.monitoring import MetricsCollector, HealthChecker
from gofastapi.ai_debugger import ErrorTranslator, InteractiveDebugger


@pytest.fixture
def app():
    """Create a test GoFastAPI application."""
    return GoFastAPI(
        title="Test App",
        version="1.0.0",
        debug=True
    )


@pytest.fixture
def test_client(app):
    """Create a test client for the app."""
    from gofastapi.testing import TestClient
    return TestClient(app)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def python_bridge():
    """Create a mock Python bridge."""
    bridge = Mock(spec=PythonBridge)
    bridge.call_python.return_value = {"result": "success"}
    bridge.is_connected.return_value = True
    return bridge


@pytest.fixture
def hot_reloader(app, temp_dir):
    """Create a hot reloader instance."""
    return HotReloader(app, watch_dirs=[str(temp_dir)])


@pytest.fixture
def subinterpreter_manager():
    """Create a subinterpreter manager."""
    manager = Mock(spec=SubinterpreterManager)
    manager.execute.return_value = "executed"
    manager.get_pool_size.return_value = 10
    manager.get_active_count.return_value = 5
    return manager


@pytest.fixture
def metrics_collector(app):
    """Create a metrics collector."""
    return MetricsCollector(app)


@pytest.fixture
def health_checker(app):
    """Create a health checker."""
    return HealthChecker(app)


@pytest.fixture
def error_translator():
    """Create an error translator."""
    translator = Mock(spec=ErrorTranslator)
    translator.translate_error.return_value = "AI translated error"
    translator.get_suggestions.return_value = ["suggestion 1", "suggestion 2"]
    return translator


@pytest.fixture
def interactive_debugger():
    """Create an interactive debugger."""
    debugger = Mock(spec=InteractiveDebugger)
    debugger.start_session.return_value = "debug_session_id"
    debugger.execute_debug_code.return_value = "debug result"
    return debugger


@pytest.fixture
def sample_route_data():
    """Sample route data for testing."""
    return {
        "path": "/users/{user_id}",
        "method": "GET",
        "handler": "get_user",
        "parameters": {
            "user_id": {"type": "int", "required": True}
        },
        "response": {
            "type": "dict",
            "example": {"user_id": 123, "name": "John Doe"}
        }
    }


@pytest.fixture
def sample_performance_data():
    """Sample performance test data."""
    return {
        "requests_per_second": 50000,
        "latency_p50": 1.2,
        "latency_p95": 2.8,
        "latency_p99": 4.5,
        "memory_usage_mb": 45,
        "cpu_usage_percent": 25,
        "error_rate": 0.001
    }


# Mock external dependencies
@pytest.fixture(autouse=True)
def mock_external_deps(monkeypatch):
    """Mock external dependencies for all tests."""
    # Mock Go binary execution
    mock_go_binary = MagicMock()
    mock_go_binary.communicate.return_value = (b"Go binary output", b"")
    mock_go_binary.returncode = 0
    
    def mock_popen(*args, **kwargs):
        return mock_go_binary
    
    monkeypatch.setattr("subprocess.Popen", mock_popen)
    
    # Mock file system operations where needed
    original_exists = Path.exists
    
    def mock_exists(self):
        # Mock Go binary existence
        if "gofastapi_server" in str(self):
            return True
        return original_exists(self)
    
    monkeypatch.setattr(Path, "exists", mock_exists)


# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Pytest configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add unit marker to tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests in integration directory
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add performance marker to performance tests
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)


# Async test support
@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
