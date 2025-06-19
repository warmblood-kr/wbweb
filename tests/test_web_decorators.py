"""
Test web decorators for content negotiation and error handling.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from starlette.requests import Request
from starlette.responses import HTMLResponse


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


class MockRenderer:
    """Mock renderer for testing decorators."""
    
    def __init__(self, return_data=None, return_component=None):
        self.return_data = return_data
        self.return_component = return_component
        
    def render(self, request, **kwargs):
        if self.return_data is not None:
            return self.return_data
        if self.return_component is not None:
            return self.return_component
        return ['div', {}, 'Default response']


class TestWebDecoratorsImports:
    """Test that web decorators can be imported correctly."""
    
    def test_import_from_web_module(self):
        """Test importing decorators from web module."""
        from wbweb.core.web import content_negotiation, render_error_response
        assert content_negotiation is not None
        assert render_error_response is not None
        
    def test_import_from_main_package(self):
        """Test importing from main wbweb package."""
        from wbweb import content_negotiation, render_error_response
        assert content_negotiation is not None
        assert render_error_response is not None


class TestContentNegotiationDecorator:
    """Test the content_negotiation decorator."""
    
    @pytest.mark.asyncio
    async def test_decorator_with_json_response(self):
        """Test decorator handling JSON response from renderer."""
        from wbweb.core.web.decorators import content_negotiation
        
        # Mock renderer that returns dict (JSON response)
        json_data = {'message': 'success', 'data': [1, 2, 3]}
        mock_renderer_class = lambda: MockRenderer(return_data=json_data)
        
        @content_negotiation(mock_renderer_class)
        async def test_view(request):
            return {'test_data': 'hello', 'status_code': 201}
        
        request = MockRequest()
        response = await test_view(request)
        
        # Should return HTMLResponse with JSON content
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 201
        
        # Response body should be JSON string
        import json
        expected_json = json.dumps(json_data)
        assert response.body.decode() == expected_json
    
    @pytest.mark.asyncio 
    async def test_decorator_with_html_component(self):
        """Test decorator handling HTML component from renderer."""
        from wbweb.core.web.decorators import content_negotiation
        
        # Mock renderer that returns hiccup component
        component = ['div', {'class': 'test'}, 'Hello World']
        mock_renderer_class = lambda: MockRenderer(return_component=component)
        
        @content_negotiation(mock_renderer_class)
        async def test_view(request):
            return {'test_data': 'hello', 'status_code': 200}
        
        request = MockRequest()
        
        # Mock HiccupRenderer import
        with patch('wbweb.core.templates.hiccup.HiccupRenderer') as mock_hiccup_class:
            mock_hiccup = Mock()
            mock_hiccup.render.return_value = '<div class="test">Hello World</div>'
            mock_hiccup_class.return_value = mock_hiccup
            
            response = await test_view(request)
            
            # Should return HTMLResponse with rendered HTML
            assert isinstance(response, HTMLResponse)
            assert response.status_code == 200
            assert response.body.decode() == '<div class="test">Hello World</div>'
            
            # Verify HiccupRenderer was used
            mock_hiccup_class.assert_called_once()
            mock_hiccup.render.assert_called_once_with(component)
    
    @pytest.mark.asyncio
    async def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves original function metadata."""
        from wbweb.core.web.decorators import content_negotiation
        
        mock_renderer_class = lambda: MockRenderer()
        
        @content_negotiation(mock_renderer_class)
        async def test_view_with_docstring(request):
            """This is a test view function."""
            return {'data': 'test'}
        
        # Should preserve function name and docstring
        assert test_view_with_docstring.__name__ == 'test_view_with_docstring'
        assert test_view_with_docstring.__doc__ == 'This is a test view function.'
    
    @pytest.mark.asyncio
    async def test_decorator_passes_request_data_to_renderer(self):
        """Test that decorator passes view result to renderer correctly."""
        from wbweb.core.web.decorators import content_negotiation
        
        # Mock renderer to capture what gets passed to it
        calls = []
        
        class CapturingRenderer:
            def render(self, request, **kwargs):
                calls.append((request, kwargs))
                return {'captured': True}
        
        @content_negotiation(CapturingRenderer)
        async def test_view(request):
            return {'user_id': 123, 'message': 'hello', 'status_code': 200}
        
        request = MockRequest()
        await test_view(request)
        
        # Verify renderer was called with correct arguments
        assert len(calls) == 1
        captured_request, captured_kwargs = calls[0]
        assert captured_request is request
        assert captured_kwargs == {'user_id': 123, 'message': 'hello', 'status_code': 200}
    
    @pytest.mark.asyncio
    async def test_decorator_default_status_code(self):
        """Test that decorator uses default status code when not provided."""
        from wbweb.core.web.decorators import content_negotiation
        
        mock_renderer_class = lambda: MockRenderer(return_data={'success': True})
        
        @content_negotiation(mock_renderer_class)
        async def test_view(request):
            return {'data': 'test'}  # No status_code provided
        
        request = MockRequest()
        response = await test_view(request)
        
        # Should default to 200
        assert response.status_code == 200


class TestRenderErrorResponse:
    """Test the render_error_response helper function."""
    
    def test_api_request_returns_api_message(self):
        """Test that API requests get simple message response."""
        from wbweb.core.web.decorators import render_error_response
        
        # Mock API request
        request = MockRequest(api_client='true')
        
        response = render_error_response(
            request=request,
            api_message="Not found",
            ui_html="<h1>404 - Not Found</h1><p>The page you requested was not found.</p>",
            status_code=404
        )
        
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 404
        assert response.body.decode() == "Not found"
    
    def test_browser_request_returns_html(self):
        """Test that browser requests get rich HTML response."""
        from wbweb.core.web.decorators import render_error_response
        
        # Mock browser request (no special headers)
        request = MockRequest()
        
        response = render_error_response(
            request=request,
            api_message="Server error",
            ui_html="<h1>500 - Server Error</h1><p>Something went wrong on our end.</p>",
            status_code=500
        )
        
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 500
        assert response.body.decode() == "<h1>500 - Server Error</h1><p>Something went wrong on our end.</p>"
    
    def test_htmx_request_returns_api_message(self):
        """Test that HTMX requests are treated as API requests."""
        from wbweb.core.web.decorators import render_error_response
        
        # Mock HTMX request
        request = MockRequest(hx_request='true')
        
        response = render_error_response(
            request=request,
            api_message="Validation failed",
            ui_html="<div class='error'>Validation failed</div>",
            status_code=400
        )
        
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 400
        assert response.body.decode() == "Validation failed"
    
    def test_custom_status_codes(self):
        """Test that custom status codes are preserved."""
        from wbweb.core.web.decorators import render_error_response
        
        request = MockRequest()
        
        # Test various status codes
        for status_code in [201, 301, 403, 422, 503]:
            response = render_error_response(
                request=request,
                api_message=f"Status {status_code}",
                ui_html=f"<h1>Status {status_code}</h1>",
                status_code=status_code
            )
            assert response.status_code == status_code


class TestDecoratorIntegration:
    """Test integration between decorators and other framework components."""
    
    @pytest.mark.asyncio
    async def test_decorator_works_with_actual_renderer_classes(self):
        """Test decorator integration with actual framework renderer classes."""
        from wbweb.core.web.decorators import content_negotiation
        from wbweb.core.templates import DefaultRenderer
        
        # Create a test renderer class
        class TestRenderer(DefaultRenderer):
            def render_ui(self, **kwargs):
                return ['div', {}, f"UI: {kwargs.get('message', 'default')}"]
            
            def render_api(self, **kwargs):
                return ['span', {}, f"API: {kwargs.get('message', 'default')}"]
        
        @content_negotiation(TestRenderer)
        async def test_endpoint(request):
            return {'message': 'Hello World', 'status_code': 200}
        
        # Test with browser request (should get HTML)
        browser_request = MockRequest()
        
        with patch('wbweb.core.templates.hiccup.HiccupRenderer') as mock_hiccup_class:
            mock_hiccup = Mock()
            mock_hiccup.render.return_value = '<div>UI: Hello World</div>'
            mock_hiccup_class.return_value = mock_hiccup
            
            response = await test_endpoint(browser_request)
            
            assert isinstance(response, HTMLResponse)
            assert response.status_code == 200
            assert '<div>UI: Hello World</div>' in response.body.decode()


class TestDecoratorErrorHandling:
    """Test error handling in decorators."""
    
    @pytest.mark.asyncio
    async def test_decorator_handles_renderer_exceptions(self):
        """Test that decorator properly handles exceptions from renderers."""
        from wbweb.core.web.decorators import content_negotiation
        
        class BrokenRenderer:
            def render(self, request, **kwargs):
                raise ValueError("Renderer error")
        
        @content_negotiation(BrokenRenderer)
        async def test_view(request):
            return {'data': 'test'}
        
        request = MockRequest()
        
        # Should propagate the renderer exception
        with pytest.raises(ValueError, match="Renderer error"):
            await test_view(request)
    
    @pytest.mark.asyncio
    async def test_decorator_handles_view_exceptions(self):
        """Test that decorator properly handles exceptions from view functions."""
        from wbweb.core.web.decorators import content_negotiation
        
        mock_renderer_class = lambda: MockRenderer()
        
        @content_negotiation(mock_renderer_class)
        async def broken_view(request):
            raise RuntimeError("View error")
        
        request = MockRequest()
        
        # Should propagate the view exception
        with pytest.raises(RuntimeError, match="View error"):
            await broken_view(request)