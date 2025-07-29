"""Unit tests for GoFastAPI core functionality."""

import pytest
from unittest.mock import Mock, patch
from gofastapi import GoFastAPI


class TestGoFastAPI:
    """Test the main GoFastAPI class."""
    
    def test_app_creation(self):
        """Test basic app creation."""
        app = GoFastAPI(title="Test App", version="1.0.0")
        assert app.title == "Test App"
        assert app.version == "1.0.0"
    
    def test_app_with_debug(self):
        """Test app creation with debug mode."""
        app = GoFastAPI(debug=True)
        assert app.debug is True
    
    def test_route_decorator(self, app):
        """Test route decorator functionality."""
        @app.get("/test")
        def test_route():
            return {"message": "test"}
        
        # Check if route was registered
        assert "/test" in [route.path for route in app.routes]
    
    def test_multiple_routes(self, app):
        """Test multiple route registration."""
        @app.get("/users")
        def get_users():
            return {"users": []}
        
        @app.post("/users")
        def create_user():
            return {"user": "created"}
        
        @app.get("/users/{user_id}")
        def get_user(user_id: int):
            return {"user_id": user_id}
        
        assert len(app.routes) == 3
    
    def test_middleware(self, app):
        """Test middleware functionality."""
        middleware_called = False
        
        @app.middleware("request")
        async def test_middleware(request, call_next):
            nonlocal middleware_called
            middleware_called = True
            response = await call_next(request)
            return response
        
        assert len(app.middleware_stack) > 0
    
    def test_error_handler(self, app):
        """Test error handler registration."""
        @app.middleware("error")
        async def error_handler(request, exc):
            return {"error": str(exc)}
        
        assert app.has_error_handler()


class TestRouting:
    """Test routing functionality."""
    
    def test_get_route(self, app):
        """Test GET route."""
        @app.get("/items")
        def get_items():
            return {"items": []}
        
        route = app.get_route("/items", "GET")
        assert route is not None
        assert route.method == "GET"
    
    def test_post_route(self, app):
        """Test POST route."""
        @app.post("/items")
        def create_item(item: dict):
            return {"created": item}
        
        route = app.get_route("/items", "POST")
        assert route is not None
        assert route.method == "POST"
    
    def test_put_route(self, app):
        """Test PUT route."""
        @app.put("/items/{item_id}")
        def update_item(item_id: int, item: dict):
            return {"updated": item_id}
        
        route = app.get_route("/items/{item_id}", "PUT")
        assert route is not None
        assert route.method == "PUT"
    
    def test_delete_route(self, app):
        """Test DELETE route."""
        @app.delete("/items/{item_id}")
        def delete_item(item_id: int):
            return {"deleted": item_id}
        
        route = app.get_route("/items/{item_id}", "DELETE")
        assert route is not None
        assert route.method == "DELETE"
    
    def test_route_with_parameters(self, app):
        """Test route with path parameters."""
        @app.get("/users/{user_id}/posts/{post_id}")
        def get_user_post(user_id: int, post_id: int):
            return {"user_id": user_id, "post_id": post_id}
        
        route = app.get_route("/users/{user_id}/posts/{post_id}", "GET")
        assert route is not None
        assert "user_id" in route.parameters
        assert "post_id" in route.parameters


class TestConfiguration:
    """Test configuration handling."""
    
    def test_default_config(self):
        """Test default configuration values."""
        app = GoFastAPI()
        assert app.debug is False
        assert app.host == "127.0.0.1"
        assert app.port == 8000
    
    def test_custom_config(self):
        """Test custom configuration."""
        app = GoFastAPI(
            debug=True,
            host="0.0.0.0",
            port=9000,
            title="Custom App"
        )
        assert app.debug is True
        assert app.host == "0.0.0.0"
        assert app.port == 9000
        assert app.title == "Custom App"
    
    @patch.dict('os.environ', {
        'GOFASTAPI_DEBUG': 'true',
        'GOFASTAPI_HOST': '0.0.0.0',
        'GOFASTAPI_PORT': '9000'
    })
    def test_config_from_env(self):
        """Test configuration from environment variables."""
        app = GoFastAPI()
        app.load_config_from_env()
        
        assert app.debug is True
        assert app.host == "0.0.0.0"
        assert app.port == 9000


class TestValidation:
    """Test input validation."""
    
    def test_route_validation(self, app):
        """Test route parameter validation."""
        from pydantic import BaseModel
        
        class UserModel(BaseModel):
            name: str
            email: str
            age: int
        
        @app.post("/users")
        def create_user(user: UserModel):
            return {"user": user.dict()}
        
        route = app.get_route("/users", "POST")
        assert route is not None
        # Validation logic would be tested in integration tests
    
    def test_response_validation(self, app):
        """Test response validation."""
        @app.get("/users/{user_id}")
        def get_user(user_id: int) -> dict:
            return {"user_id": user_id, "name": "John Doe"}
        
        route = app.get_route("/users/{user_id}", "GET")
        assert route is not None
        assert route.response_type == dict


class TestStartupShutdown:
    """Test startup and shutdown events."""
    
    def test_startup_event(self, app):
        """Test startup event handler."""
        startup_called = False
        
        @app.on_event("startup")
        async def startup():
            nonlocal startup_called
            startup_called = True
        
        assert len(app.startup_handlers) > 0
    
    def test_shutdown_event(self, app):
        """Test shutdown event handler."""
        shutdown_called = False
        
        @app.on_event("shutdown")
        async def shutdown():
            nonlocal shutdown_called
            shutdown_called = True
        
        assert len(app.shutdown_handlers) > 0
    
    def test_multiple_startup_handlers(self, app):
        """Test multiple startup handlers."""
        @app.on_event("startup")
        async def startup1():
            pass
        
        @app.on_event("startup")
        async def startup2():
            pass
        
        assert len(app.startup_handlers) == 2
