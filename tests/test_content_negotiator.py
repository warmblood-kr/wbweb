"""
Test ContentNegotiator extraction and functionality.
"""

class MockRequest:
    """Mock request for testing without starlette dependency."""
    
    def __init__(self, headers=None):
        self.headers = headers or {}
        
    def get(self, key, default=None):
        return self.headers.get(key, default)


class TestContentNegotiator:
    """Test ContentNegotiator functionality."""
    
    def test_import_works(self):
        """Test that ContentNegotiator can be imported."""
        from wbweb.core.web import ContentNegotiator
        assert ContentNegotiator is not None
        
    def test_package_level_import(self):
        """Test importing from main package."""
        from wbweb import ContentNegotiator
        assert ContentNegotiator is not None
        
    def test_is_api_request_with_api_header(self):
        """Test API client detection via x-api-client header."""
        from wbweb.core.web import ContentNegotiator
        
        # Mock request with API header
        class MockHeaders:
            def get(self, key, default=None):
                if key == 'x-api-client':
                    return 'true'
                return default
                
        class MockRequest:
            def __init__(self):
                self.headers = MockHeaders()
        
        request = MockRequest()
        assert ContentNegotiator.is_api_request(request) == True
        
    def test_is_api_request_with_htmx_header(self):
        """Test API client detection via hx-request header."""
        from wbweb.core.web import ContentNegotiator
        
        class MockHeaders:
            def get(self, key, default=None):
                if key == 'hx-request':
                    return 'true'
                return default
                
        class MockRequest:
            def __init__(self):
                self.headers = MockHeaders()
        
        request = MockRequest()
        assert ContentNegotiator.is_api_request(request) == True
        
    def test_is_api_request_browser(self):
        """Test browser client detection (no special headers)."""
        from wbweb.core.web import ContentNegotiator
        
        class MockHeaders:
            def get(self, key, default=None):
                return default
                
        class MockRequest:
            def __init__(self):
                self.headers = MockHeaders()
        
        request = MockRequest()
        assert ContentNegotiator.is_api_request(request) == False
        
    def test_get_renderer_returns_renderers(self):
        """Test that get_renderer returns appropriate renderer types."""
        from wbweb.core.web import ContentNegotiator
        from wbweb.core.templates import UIRenderer, ApiRenderer
        
        # API request
        class MockHeaders:
            def get(self, key, default=None):
                if key == 'x-api-client':
                    return 'true'
                return default
                
        class MockApiRequest:
            def __init__(self):
                self.headers = MockHeaders()
        
        api_request = MockApiRequest()
        api_renderer = ContentNegotiator.get_renderer(api_request)
        assert isinstance(api_renderer, ApiRenderer)
        
        # Browser request
        class MockBrowserHeaders:
            def get(self, key, default=None):
                return default
                
        class MockBrowserRequest:
            def __init__(self):
                self.headers = MockBrowserHeaders()
        
        browser_request = MockBrowserRequest()
        ui_renderer = ContentNegotiator.get_renderer(browser_request)
        assert isinstance(ui_renderer, UIRenderer)