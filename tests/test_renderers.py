"""
Test renderer strategy classes extraction and functionality.
"""

import json


class MockRequest:
    """Mock request for testing without starlette dependency."""
    
    def __init__(self, accept_header=None, api_client=None, hx_request=None):
        self.headers = MockHeaders(accept_header, api_client, hx_request)

class MockHeaders:
    """Mock headers for testing."""
    
    def __init__(self, accept_header=None, api_client=None, hx_request=None):
        self._headers = {}
        if accept_header:
            self._headers['accept'] = accept_header
        if api_client:
            self._headers['x-api-client'] = api_client
        if hx_request:
            self._headers['hx-request'] = hx_request
    
    def get(self, key, default=None):
        return self._headers.get(key, default)


class TestRendererImports:
    """Test that renderers can be imported correctly."""
    
    def test_import_from_templates_module(self):
        """Test importing renderers from templates module."""
        from wbweb.core.templates import DefaultRenderer, UIRenderer, ApiRenderer
        assert DefaultRenderer is not None
        assert UIRenderer is not None  
        assert ApiRenderer is not None
        
    def test_import_from_main_package(self):
        """Test importing from main wbweb package."""
        from wbweb import DefaultRenderer, UIRenderer, ApiRenderer
        assert DefaultRenderer is not None
        assert UIRenderer is not None
        assert ApiRenderer is not None


class TestUIRendererAndApiRenderer:
    """Test the simple renderer strategy classes."""
    
    def test_ui_renderer_inherits_hiccup(self):
        """Test UIRenderer inherits from HiccupRenderer."""
        from wbweb.core.templates import UIRenderer, HiccupRenderer
        
        renderer = UIRenderer()
        assert isinstance(renderer, HiccupRenderer)
        
        # Test it can render hiccup
        result = renderer.render(['p', {}, 'UI content'])
        assert result == '<p>UI content</p>\n'
        
    def test_api_renderer_inherits_hiccup(self):
        """Test ApiRenderer inherits from HiccupRenderer."""
        from wbweb.core.templates import ApiRenderer, HiccupRenderer
        
        renderer = ApiRenderer()
        assert isinstance(renderer, HiccupRenderer)
        
        # Test it can render hiccup
        result = renderer.render(['div', {'class': 'api'}, 'API content'])
        assert result == '<div class="api">API content</div>\n'


class TestDefaultRenderer:
    """Test DefaultRenderer content negotiation logic."""
    
    def test_html_accept_header(self):
        """Test HTML Accept header routing."""
        from wbweb.core.templates import DefaultRenderer
        
        class TestDefaultRenderer(DefaultRenderer):
            def render_ui(self, request, **kwargs):
                return ['p', {}, 'UI response']
                
        renderer = TestDefaultRenderer()
        request = MockRequest(accept_header='text/html')
        
        result = renderer.render(request, test_data='hello')
        content = result['content']
        assert content == '''<p>UI response</p>\n'''
        
    def test_json_accept_header(self):
        """Test JSON Accept header routing."""
        from wbweb.core.templates import DefaultRenderer
        
        class TestDefaultRenderer(DefaultRenderer):
            def render_api(self, request, **kwargs):
                return ['div', {'class': 'api'}, 'API response']
                
        renderer = TestDefaultRenderer()
        request = MockRequest(accept_header='application/json')
        
        result = renderer.render(request, test_data='hello')

        content = json.loads(result['content'])
        
        # Should get JSON representation
        assert content == ['div', {'class': 'api'}, 'API response']

    def test_api_client_header_routing(self):
        """Test x-api-client header routing."""
        from wbweb.core.templates import DefaultRenderer
        
        class TestDefaultRenderer(DefaultRenderer):
            def render_api(self, request, **kwargs):
                return ['span', {}, 'Legacy API']
                
        renderer = TestDefaultRenderer()
        request = MockRequest()
        request.headers = {'accept': 'application/xml'}
        
        result = renderer.render(request)
        content = json.loads(result['content'])

        assert content == ['span', {}, 'Legacy API']

    def test_raw_accept_header(self):
        """Test raw Accept header routing."""
        from wbweb.core.templates import DefaultRenderer
        
        renderer = DefaultRenderer()
        request = MockRequest(accept_header='application/raw')
        
        result = renderer.render(request, debug_data='test', number=42)
        
        # Should get JSON string
        content = result['content']

        assert content == {
            'debug_data': 'test',
            'number': 42,
        }

    def test_default_fallback(self):
        """Test default fallback to UI rendering."""
        from wbweb.core.templates import DefaultRenderer
        
        class TestDefaultRenderer(DefaultRenderer):
            def render_ui(self, request, **kwargs):
                return ['main', {}, 'Default UI']
                
        renderer = TestDefaultRenderer()
        request = MockRequest()  # No special headers
        
        result = renderer.render(request)
        content = result['content']
        assert content == '<main>Default UI</main>\n'
