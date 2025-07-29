"""Performance benchmarks for GoFastAPI."""

import pytest
import time
import asyncio
import statistics
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    @pytest.mark.performance
    def test_request_throughput(self, test_client):
        """Benchmark request throughput."""
        @test_client.app.get("/benchmark")
        def benchmark_endpoint():
            return {"status": "ok", "timestamp": time.time()}
        
        # Warm up
        for _ in range(100):
            test_client.get("/benchmark")
        
        # Benchmark
        start_time = time.time()
        request_count = 1000
        
        for _ in range(request_count):
            response = test_client.get("/benchmark")
            assert response.status_code == 200
        
        end_time = time.time()
        duration = end_time - start_time
        rps = request_count / duration
        
        print(f"Requests per second: {rps:.2f}")
        # Should be fast (this is a mock test, real GoFastAPI would be much faster)
        assert rps > 100  # Minimum expected RPS in test environment
    
    @pytest.mark.performance
    def test_concurrent_requests(self, test_client):
        """Benchmark concurrent request handling."""
        @test_client.app.get("/concurrent")
        def concurrent_endpoint():
            time.sleep(0.01)  # Simulate small delay
            return {"processed": True}
        
        def make_request():
            response = test_client.get("/concurrent")
            return response.status_code == 200
        
        # Test with multiple threads
        thread_count = 50
        requests_per_thread = 10
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            for _ in range(thread_count * requests_per_thread):
                future = executor.submit(make_request)
                futures.append(future)
            
            # Wait for all requests to complete
            results = [future.result() for future in futures]
        
        end_time = time.time()
        duration = end_time - start_time
        total_requests = len(results)
        rps = total_requests / duration
        
        print(f"Concurrent RPS: {rps:.2f}")
        print(f"Total requests: {total_requests}")
        print(f"Duration: {duration:.2f}s")
        
        # All requests should succeed
        assert all(results)
        # Should handle concurrency well
        assert rps > 50
    
    @pytest.mark.performance
    def test_latency_distribution(self, test_client):
        """Test response latency distribution."""
        @test_client.app.get("/latency")
        def latency_endpoint():
            return {"response": "data"}
        
        latencies = []
        request_count = 100
        
        for _ in range(request_count):
            start_time = time.perf_counter()
            response = test_client.get("/latency")
            end_time = time.perf_counter()
            
            assert response.status_code == 200
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
        
        # Calculate statistics
        mean_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        p95_latency = sorted(latencies)[int(0.95 * len(latencies))]
        p99_latency = sorted(latencies)[int(0.99 * len(latencies))]
        
        print(f"Mean latency: {mean_latency:.2f}ms")
        print(f"Median latency: {median_latency:.2f}ms")
        print(f"P95 latency: {p95_latency:.2f}ms")
        print(f"P99 latency: {p99_latency:.2f}ms")
        
        # Latency should be reasonable
        assert mean_latency < 100  # Less than 100ms mean
        assert p95_latency < 200   # Less than 200ms P95
    
    @pytest.mark.performance
    def test_memory_usage(self, test_client):
        """Test memory usage under load."""
        import psutil
        import os
        
        @test_client.app.get("/memory")
        def memory_endpoint():
            # Create some data to process
            data = {"items": list(range(1000))}
            return data
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Make many requests
        request_count = 500
        for _ in range(request_count):
            response = test_client.get("/memory")
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        memory_growth_mb = memory_growth / (1024 * 1024)
        
        print(f"Initial memory: {initial_memory / (1024 * 1024):.2f}MB")
        print(f"Final memory: {final_memory / (1024 * 1024):.2f}MB")
        print(f"Memory growth: {memory_growth_mb:.2f}MB")
        
        # Memory growth should be reasonable
        assert memory_growth_mb < 50  # Less than 50MB growth
    
    @pytest.mark.performance
    def test_json_serialization_performance(self, test_client):
        """Test JSON serialization performance."""
        large_data = {
            "users": [
                {
                    "id": i,
                    "name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "metadata": {"key": f"value_{i}", "number": i * 2}
                }
                for i in range(1000)
            ],
            "pagination": {"page": 1, "limit": 1000, "total": 1000}
        }
        
        @test_client.app.get("/large-json")
        def large_json_endpoint():
            return large_data
        
        # Benchmark JSON serialization
        times = []
        for _ in range(10):
            start_time = time.perf_counter()
            response = test_client.get("/large-json")
            end_time = time.perf_counter()
            
            assert response.status_code == 200
            duration = (end_time - start_time) * 1000
            times.append(duration)
        
        avg_time = statistics.mean(times)
        print(f"Average JSON serialization time: {avg_time:.2f}ms")
        
        # Should serialize large JSON quickly
        assert avg_time < 100  # Less than 100ms for 1000 items
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_stress_test(self, test_client):
        """Stress test with high load."""
        @test_client.app.get("/stress")
        def stress_endpoint():
            return {"status": "ok"}
        
        @test_client.app.post("/stress")
        def stress_post_endpoint(data: dict):
            return {"received": len(str(data))}
        
        # High load test
        total_requests = 1000
        get_requests = total_requests // 2
        post_requests = total_requests // 2
        
        start_time = time.time()
        
        # Mixed GET and POST requests
        for i in range(total_requests):
            if i % 2 == 0:
                response = test_client.get("/stress")
            else:
                response = test_client.post("/stress", json={"data": f"test_{i}"})
            
            assert response.status_code == 200
        
        end_time = time.time()
        duration = end_time - start_time
        rps = total_requests / duration
        
        print(f"Stress test RPS: {rps:.2f}")
        print(f"Total requests: {total_requests}")
        print(f"Duration: {duration:.2f}s")
        
        # Should handle stress reasonably
        assert rps > 50
    
    @pytest.mark.performance
    def test_subinterpreter_performance(self, test_client, subinterpreter_manager):
        """Test subinterpreter execution performance."""
        @test_client.app.post("/execute")
        def execute_endpoint(code: str):
            result = subinterpreter_manager.execute(code)
            return {"result": result}
        
        # Test code execution performance
        test_code = "sum(range(100))"
        times = []
        
        for _ in range(50):
            start_time = time.perf_counter()
            response = test_client.post("/execute", json={"code": test_code})
            end_time = time.perf_counter()
            
            assert response.status_code == 200
            duration = (end_time - start_time) * 1000
            times.append(duration)
        
        avg_time = statistics.mean(times)
        print(f"Average subinterpreter execution time: {avg_time:.2f}ms")
        
        # Should execute code quickly
        assert avg_time < 50  # Less than 50ms average


class BenchmarkResults:
    """Store and analyze benchmark results."""
    
    def __init__(self):
        self.results = {}
    
    def add_result(self, test_name: str, metric: str, value: float):
        """Add a benchmark result."""
        if test_name not in self.results:
            self.results[test_name] = {}
        self.results[test_name][metric] = value
    
    def compare_with_baseline(self, baseline_file: str = None):
        """Compare results with baseline."""
        if not baseline_file:
            return
        
        # Load baseline results
        try:
            import json
            with open(baseline_file, 'r') as f:
                baseline = json.load(f)
            
            # Compare results
            for test_name, metrics in self.results.items():
                if test_name in baseline:
                    for metric, value in metrics.items():
                        if metric in baseline[test_name]:
                            baseline_value = baseline[test_name][metric]
                            improvement = (value / baseline_value) * 100
                            print(f"{test_name}.{metric}: {improvement:.1f}% of baseline")
        except FileNotFoundError:
            print(f"Baseline file {baseline_file} not found")
    
    def save_results(self, filename: str):
        """Save benchmark results to file."""
        import json
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)


@pytest.fixture
def benchmark_results():
    """Fixture for collecting benchmark results."""
    return BenchmarkResults()
