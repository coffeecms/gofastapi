"""Test fixtures and sample data."""

import pytest
import json
from pathlib import Path


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": 123,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 30,
        "active": True,
        "roles": ["user", "admin"],
        "metadata": {
            "created_at": "2024-01-15T10:30:00Z",
            "last_login": "2024-01-20T14:45:00Z"
        }
    }


@pytest.fixture
def sample_api_response():
    """Sample API response data."""
    return {
        "status": "success",
        "data": {
            "items": [
                {"id": 1, "name": "Item 1", "value": 100},
                {"id": 2, "name": "Item 2", "value": 200},
                {"id": 3, "name": "Item 3", "value": 300}
            ],
            "pagination": {
                "page": 1,
                "limit": 10,
                "total": 3,
                "has_next": False
            }
        },
        "timestamp": "2024-01-15T10:30:00Z"
    }


@pytest.fixture
def large_dataset():
    """Large dataset for performance testing."""
    return {
        "users": [
            {
                "id": i,
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "score": i * 10,
                "active": i % 2 == 0
            }
            for i in range(1000)
        ]
    }


@pytest.fixture
def error_scenarios():
    """Common error scenarios for testing."""
    return [
        {
            "name": "validation_error",
            "input": {"name": "", "email": "invalid-email"},
            "expected_status": 422,
            "expected_error": "Validation error"
        },
        {
            "name": "not_found",
            "input": {"user_id": 99999},
            "expected_status": 404,
            "expected_error": "User not found"
        },
        {
            "name": "permission_denied",
            "input": {"action": "delete", "user_id": 1},
            "expected_status": 403,
            "expected_error": "Permission denied"
        }
    ]


@pytest.fixture
def mock_database_data():
    """Mock database data."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
            {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
        ],
        "posts": [
            {"id": 1, "user_id": 1, "title": "First Post", "content": "Hello World"},
            {"id": 2, "user_id": 2, "title": "Second Post", "content": "Testing"}
        ],
        "comments": [
            {"id": 1, "post_id": 1, "user_id": 2, "content": "Great post!"},
            {"id": 2, "post_id": 1, "user_id": 3, "content": "Thanks for sharing"}
        ]
    }


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "server": {
            "host": "127.0.0.1",
            "port": 8000,
            "debug": True,
            "workers": 1
        },
        "database": {
            "url": "sqlite:///:memory:",
            "echo": False
        },
        "cache": {
            "backend": "memory",
            "ttl": 300
        },
        "monitoring": {
            "enabled": True,
            "metrics_port": 9090
        },
        "ai_debugger": {
            "enabled": True,
            "model": "mock",
            "confidence_threshold": 0.8
        }
    }


@pytest.fixture
def sample_routes():
    """Sample route definitions."""
    return [
        {
            "path": "/",
            "method": "GET",
            "handler": "root",
            "description": "Root endpoint"
        },
        {
            "path": "/users",
            "method": "GET",
            "handler": "list_users",
            "description": "List all users"
        },
        {
            "path": "/users/{user_id}",
            "method": "GET",
            "handler": "get_user",
            "description": "Get user by ID"
        },
        {
            "path": "/users",
            "method": "POST",
            "handler": "create_user",
            "description": "Create new user"
        },
        {
            "path": "/users/{user_id}",
            "method": "PUT",
            "handler": "update_user",
            "description": "Update user"
        },
        {
            "path": "/users/{user_id}",
            "method": "DELETE",
            "handler": "delete_user",
            "description": "Delete user"
        }
    ]


@pytest.fixture
def performance_baseline():
    """Performance baseline data."""
    return {
        "requests_per_second": 50000,
        "latency_p50": 1.2,
        "latency_p95": 2.8,
        "latency_p99": 4.5,
        "memory_usage_mb": 45,
        "cpu_usage_percent": 25,
        "error_rate": 0.001,
        "concurrent_users": 1000,
        "response_time_avg": 2.1
    }


class DataGenerator:
    """Utility class for generating test data."""
    
    @staticmethod
    def generate_users(count: int = 100):
        """Generate user test data."""
        return [
            {
                "id": i,
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "age": 20 + (i % 50),
                "active": i % 3 != 0,
                "created_at": f"2024-01-{(i % 28) + 1:02d}T10:30:00Z"
            }
            for i in range(1, count + 1)
        ]
    
    @staticmethod
    def generate_api_calls(count: int = 50):
        """Generate API call test data."""
        methods = ["GET", "POST", "PUT", "DELETE"]
        endpoints = ["/users", "/posts", "/comments", "/analytics"]
        
        return [
            {
                "id": i,
                "method": methods[i % len(methods)],
                "endpoint": endpoints[i % len(endpoints)],
                "status_code": 200 if i % 10 != 0 else 404,
                "response_time": 1.0 + (i % 5) * 0.5,
                "timestamp": f"2024-01-15T{(i % 24):02d}:30:00Z"
            }
            for i in range(count)
        ]
    
    @staticmethod
    def generate_metrics(count: int = 100):
        """Generate metrics test data."""
        import random
        
        return [
            {
                "timestamp": f"2024-01-15T10:{i:02d}:00Z",
                "cpu_percent": random.uniform(10, 80),
                "memory_mb": random.uniform(40, 60),
                "requests_per_second": random.uniform(1000, 5000),
                "active_connections": random.randint(50, 200),
                "error_rate": random.uniform(0, 0.01)
            }
            for i in range(count)
        ]


@pytest.fixture
def data_generator():
    """Data generator fixture."""
    return DataGenerator()


def load_test_data(filename: str):
    """Load test data from JSON file."""
    current_dir = Path(__file__).parent
    file_path = current_dir / filename
    
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        return {}


def save_test_data(data: dict, filename: str):
    """Save test data to JSON file."""
    current_dir = Path(__file__).parent
    file_path = current_dir / filename
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


# Sample test data files
TEST_DATA = {
    "sample_requests.json": {
        "requests": [
            {"method": "GET", "path": "/", "expected": 200},
            {"method": "GET", "path": "/users", "expected": 200},
            {"method": "POST", "path": "/users", "data": {"name": "Test"}, "expected": 201},
            {"method": "GET", "path": "/users/1", "expected": 200},
            {"method": "PUT", "path": "/users/1", "data": {"name": "Updated"}, "expected": 200},
            {"method": "DELETE", "path": "/users/1", "expected": 204}
        ]
    },
    "error_cases.json": {
        "errors": [
            {"path": "/users/999", "method": "GET", "expected_status": 404},
            {"path": "/users", "method": "POST", "data": {}, "expected_status": 422},
            {"path": "/admin", "method": "GET", "expected_status": 403}
        ]
    },
    "performance_data.json": {
        "benchmarks": [
            {"name": "basic_get", "rps": 50000, "latency": 1.2},
            {"name": "json_post", "rps": 45000, "latency": 1.8},
            {"name": "database_query", "rps": 30000, "latency": 2.5}
        ]
    }
}


# Create test data files if they don't exist
def create_test_data_files():
    """Create test data files in fixtures directory."""
    current_dir = Path(__file__).parent
    
    for filename, data in TEST_DATA.items():
        file_path = current_dir / filename
        if not file_path.exists():
            save_test_data(data, filename)
