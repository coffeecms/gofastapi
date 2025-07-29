"""Integration tests for GoFastAPI application."""

import pytest
import time
import json
from unittest.mock import patch


class TestApplicationIntegration:
    """Test full application integration."""
    
    def test_basic_request_response(self, test_client):
        """Test basic request-response cycle."""
        @test_client.app.get("/")
        def root():
            return {"message": "Hello GoFastAPI!"}
        
        response = test_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello GoFastAPI!"}
    
    def test_path_parameters(self, test_client):
        """Test path parameter handling."""
        @test_client.app.get("/users/{user_id}")
        def get_user(user_id: int):
            return {"user_id": user_id}
        
        response = test_client.get("/users/123")
        assert response.status_code == 200
        assert response.json() == {"user_id": 123}
    
    def test_query_parameters(self, test_client):
        """Test query parameter handling."""
        @test_client.app.get("/search")
        def search(q: str, limit: int = 10):
            return {"query": q, "limit": limit}
        
        response = test_client.get("/search?q=test&limit=5")
        assert response.status_code == 200
        assert response.json() == {"query": "test", "limit": 5}
    
    def test_post_request_with_body(self, test_client):
        """Test POST request with JSON body."""
        @test_client.app.post("/users")
        def create_user(user_data: dict):
            return {"created": True, "data": user_data}
        
        user_data = {"name": "John Doe", "email": "john@example.com"}
        response = test_client.post("/users", json=user_data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["created"] is True
        assert result["data"] == user_data
    
    def test_error_handling(self, test_client):
        """Test error handling."""
        @test_client.app.get("/error")
        def error_endpoint():
            raise ValueError("Test error")
        
        response = test_client.get("/error")
        assert response.status_code >= 400


class TestRuntimeIntegration:
    """Test runtime component integration."""
    
    def test_python_bridge_integration(self, test_client, python_bridge):
        """Test Python bridge integration."""
        @test_client.app.get("/bridge")
        def bridge_test():
            result = python_bridge.call_python("test_function", {"arg": "value"})
            return result
        
        response = test_client.get("/bridge")
        assert response.status_code == 200
        assert response.json() == {"result": "success"}
    
    def test_subinterpreter_integration(self, test_client, subinterpreter_manager):
        """Test subinterpreter integration."""
        @test_client.app.post("/execute")
        def execute_code(code: str):
            result = subinterpreter_manager.execute(code)
            return {"result": result}
        
        response = test_client.post("/execute", json={"code": "print('hello')"})
        assert response.status_code == 200
        assert response.json() == {"result": "executed"}


class TestMonitoringIntegration:
    """Test monitoring integration."""
    
    def test_metrics_collection(self, test_client, metrics_collector):
        """Test metrics collection."""
        @test_client.app.get("/test")
        def test_endpoint():
            return {"test": True}
        
        @test_client.app.get("/metrics")
        def get_metrics():
            return metrics_collector.get_all_metrics()
        
        # Make a request to generate metrics
        test_client.get("/test")
        
        # Check metrics
        response = test_client.get("/metrics")
        assert response.status_code == 200
        metrics = response.json()
        assert "total_requests" in metrics
    
    def test_health_check(self, test_client, health_checker):
        """Test health check integration."""
        @test_client.app.get("/health")
        def health_check():
            status = health_checker.check_all()
            return {"status": "healthy" if status["overall"] else "unhealthy"}
        
        response = test_client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()


class TestAIDebuggingIntegration:
    """Test AI debugging integration."""
    
    def test_error_translation(self, test_client, error_translator):
        """Test error translation integration."""
        @test_client.app.middleware("error")
        async def ai_error_handler(request, exc):
            explanation = error_translator.translate_error(exc)
            return {
                "error": str(exc),
                "ai_explanation": explanation
            }
        
        @test_client.app.get("/ai-error")
        def ai_error():
            raise ValueError("Test AI error")
        
        response = test_client.get("/ai-error")
        assert response.status_code >= 400
        result = response.json()
        assert "ai_explanation" in result
        assert result["ai_explanation"] == "AI translated error"


class TestPerformanceIntegration:
    """Test performance-related integration."""
    
    @pytest.mark.slow
    def test_concurrent_requests(self, test_client):
        """Test handling concurrent requests."""
        import threading
        import time
        
        @test_client.app.get("/slow")
        def slow_endpoint():
            time.sleep(0.1)  # Simulate work
            return {"processed": True}
        
        results = []
        
        def make_request():
            response = test_client.get("/slow")
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Check results
        assert len(results) == 10
        assert all(status == 200 for status in results)
        # Should complete in reasonable time with concurrency
        assert end_time - start_time < 1.0  # Less than 1 second for 10 concurrent 0.1s requests
    
    def test_memory_usage(self, test_client):
        """Test memory usage doesn't grow excessively."""
        import psutil
        import os
        
        @test_client.app.get("/memory-test")
        def memory_test():
            # Create some data
            data = {"numbers": list(range(1000))}
            return data
        
        # Get initial memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Make multiple requests
        for _ in range(100):
            response = test_client.get("/memory-test")
            assert response.status_code == 200
        
        # Check memory hasn't grown excessively
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Allow some growth but not excessive
        assert memory_growth < 50 * 1024 * 1024  # Less than 50MB growth


class TestHotReloadIntegration:
    """Test hot-reload integration."""
    
    def test_file_watching(self, hot_reloader, temp_dir):
        """Test file watching functionality."""
        test_file = temp_dir / "test.py"
        test_file.write_text("# Test file")
        
        # Start watching
        hot_reloader.start_watching()
        
        # Modify file
        test_file.write_text("# Modified test file")
        
        # Give time for file watcher to detect change
        time.sleep(0.5)
        
        # Stop watching
        hot_reloader.stop_watching()
        
        # Check that reload was triggered (in real implementation)
        # This would check if the reload callback was called


class TestConfigurationIntegration:
    """Test configuration integration."""
    
    def test_toml_config_loading(self, temp_dir):
        """Test loading configuration from TOML file."""
        config_file = temp_dir / "gofastapi.toml"
        config_content = """
[server]
host = "0.0.0.0"
port = 9000
debug = true

[monitoring]
enabled = true
metrics_port = 9090
"""
        config_file.write_text(config_content)
        
        # In real implementation, this would load the config
        # app = GoFastAPI(config_file=str(config_file))
        # assert app.host == "0.0.0.0"
        # assert app.port == 9000
        # assert app.debug is True
    
    def test_environment_config(self):
        """Test environment variable configuration."""
        with patch.dict('os.environ', {
            'GOFASTAPI_DEBUG': 'true',
            'GOFASTAPI_HOST': '0.0.0.0',
            'GOFASTAPI_PORT': '9000'
        }):
            # In real implementation
            # app = GoFastAPI()
            # app.load_config_from_env()
            # assert app.debug is True
            pass


class TestDatabaseIntegration:
    """Test database integration (if applicable)."""
    
    @pytest.mark.skip(reason="Database not configured")
    def test_database_connection(self, test_client):
        """Test database connection."""
        @test_client.app.get("/db-test")
        def db_test():
            # In real implementation, this would test database connection
            return {"db_connected": True}
        
        response = test_client.get("/db-test")
        assert response.status_code == 200
        assert response.json()["db_connected"] is True


class TestExternalAPIIntegration:
    """Test external API integration."""
    
    @patch('requests.get')
    def test_external_api_call(self, mock_get, test_client):
        """Test calling external API."""
        mock_get.return_value.json.return_value = {"external": "data"}
        mock_get.return_value.status_code = 200
        
        @test_client.app.get("/external")
        def external_api():
            import requests
            response = requests.get("https://api.example.com/data")
            return response.json()
        
        response = test_client.get("/external")
        assert response.status_code == 200
        assert response.json() == {"external": "data"}
