"""
Test content negotiation functionality via get_preferred_format.
"""

class MockRequest:
    """Mock request for testing without starlette dependency."""
    
    def __init__(self, headers=None):
        self.headers = headers or {}
        
    def get(self, key, default=None):
        return self.headers.get(key, default)


class TestContentNegotiation:
    """Test content negotiation functionality."""
    
    def test_get_preferred_format_json(self):
        """Test JSON format detection via Accept header."""
        from wbweb.core.templates.renderers import get_preferred_format
        
        class MockHeaders:
            def get(self, key, default=None):
                if key == 'accept':
                    return 'application/json'
                return default
                
        class MockRequest:
            def __init__(self):
                self.headers = MockHeaders()
        
        request = MockRequest()
        assert get_preferred_format(request) == 'json'
        
    def test_get_preferred_format_html(self):
        """Test HTML format detection via Accept header."""
        from wbweb.core.templates.renderers import get_preferred_format
        
        class MockHeaders:
            def get(self, key, default=None):
                if key == 'accept':
                    return 'text/html'
                return default
                
        class MockRequest:
            def __init__(self):
                self.headers = MockHeaders()
        
        request = MockRequest()
        assert get_preferred_format(request) == 'html'
        
    def test_get_preferred_format_xml(self):
        """Test XML format detection via Accept header."""
        from wbweb.core.templates.renderers import get_preferred_format
        
        class MockHeaders:
            def get(self, key, default=None):
                if key == 'accept':
                    return 'application/xml'
                return default
                
        class MockRequest:
            def __init__(self):
                self.headers = MockHeaders()
        
        request = MockRequest()
        assert get_preferred_format(request) == 'xml'
        
    def test_get_preferred_format_raw(self):
        """Test raw format detection via Accept header."""
        from wbweb.core.templates.renderers import get_preferred_format
        
        class MockHeaders:
            def get(self, key, default=None):
                if key == 'accept':
                    return 'application/raw'
                return default
                
        class MockRequest:
            def __init__(self):
                self.headers = MockHeaders()
        
        request = MockRequest()
        assert get_preferred_format(request) == 'raw'
        
    def test_get_preferred_format_default(self):
        """Test default format when no Accept header."""
        from wbweb.core.templates.renderers import get_preferred_format
        
        class MockHeaders:
            def get(self, key, default=None):
                return default
                
        class MockRequest:
            def __init__(self):
                self.headers = MockHeaders()
        
        request = MockRequest()
        assert get_preferred_format(request) == 'html'