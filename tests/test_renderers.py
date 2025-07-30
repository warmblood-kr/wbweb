"""
Test renderer strategy classes extraction and functionality.
"""

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
        assert result == '<p>UI content</p>'
        
    def test_api_renderer_inherits_hiccup(self):
        """Test ApiRenderer inherits from HiccupRenderer."""
        from wbweb.core.templates import ApiRenderer, HiccupRenderer
        
        renderer = ApiRenderer()
        assert isinstance(renderer, HiccupRenderer)
        
        # Test it can render hiccup
        result = renderer.render(['div', {'class': 'api'}, 'API content'])
        assert result == '<div class="api">API content</div>'


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
        assert result == ['p', {}, 'UI response']
        
    def test_json_accept_header(self):
        """Test JSON Accept header routing."""
        from wbweb.core.templates import DefaultRenderer
        
        class TestDefaultRenderer(DefaultRenderer):
            def render_api(self, request, **kwargs):
                return ['div', {'class': 'api'}, 'API response']
                
        renderer = TestDefaultRenderer()
        request = MockRequest(accept_header='application/json')
        
        result = renderer.render(request, test_data='hello')
        
        # Should get JSON representation
        assert isinstance(result, dict)
        assert result['component'] == 'div'
        assert result['attributes']['class'] == 'api'
        assert result['children'] == ['API response']
        
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
        assert result == ['span', {}, 'Legacy API']
        
    def test_raw_accept_header(self):
        """Test raw Accept header routing."""
        from wbweb.core.templates import DefaultRenderer
        
        renderer = DefaultRenderer()
        request = MockRequest(accept_header='application/raw')
        
        result = renderer.render(request, debug_data='test', number=42)
        
        # Should get JSON string
        assert isinstance(result, str)
        assert 'debug_data' in result
        assert 'test' in result
        assert '42' in result
        
    def test_default_fallback(self):
        """Test default fallback to UI rendering."""
        from wbweb.core.templates import DefaultRenderer
        
        class TestDefaultRenderer(DefaultRenderer):
            def render_ui(self, request, **kwargs):
                return ['main', {}, 'Default UI']
                
        renderer = TestDefaultRenderer()
        request = MockRequest()  # No special headers
        
        result = renderer.render(request)
        assert result == ['main', {}, 'Default UI']


class TestComponentToJson:
    """Test hiccup component to JSON conversion."""
    
    def test_simple_component_conversion(self):
        """Test converting simple hiccup component to JSON."""
        from wbweb.core.templates import DefaultRenderer
        
        renderer = DefaultRenderer()
        component = ['p', {}, 'Simple text']
        
        result = renderer.component_to_json(component)
        
        expected = {
            'component': 'p',
            'attributes': {},
            'children': ['Simple text']
        }
        assert result == expected
        
    def test_component_with_attributes(self):
        """Test converting component with attributes."""
        from wbweb.core.templates import DefaultRenderer
        
        renderer = DefaultRenderer()
        component = ['div', {'class': 'test', 'id': 'main'}, 'Content']
        
        result = renderer.component_to_json(component)
        
        expected = {
            'component': 'div',
            'attributes': {'class': 'test', 'id': 'main'},
            'children': ['Content']
        }
        assert result == expected
        
    def test_nested_components(self):
        """Test converting nested hiccup components."""
        from wbweb.core.templates import DefaultRenderer
        
        renderer = DefaultRenderer()
        component = [
            'div', {},
            ['p', {}, 'First paragraph'],
            ['p', {'class': 'special'}, 'Second paragraph']
        ]
        
        result = renderer.component_to_json(component)
        
        expected = {
            'component': 'div',
            'attributes': {},
            'children': [
                {
                    'component': 'p',
                    'attributes': {},
                    'children': ['First paragraph']
                },
                {
                    'component': 'p', 
                    'attributes': {'class': 'special'},
                    'children': ['Second paragraph']
                }
            ]
        }
        assert result == expected
        
    def test_plain_text_passthrough(self):
        """Test that plain text passes through unchanged."""
        from wbweb.core.templates import DefaultRenderer
        
        renderer = DefaultRenderer()
        
        result = renderer.component_to_json('Just plain text')
        assert result == 'Just plain text'
