from odoo import http
import logging
from werkzeug.wrappers import Response

_logger = logging.getLogger(__name__)


class CORSController(http.Controller):
    """Simple CORS controller for API endpoints"""
    
    def _make_cors_response(self, data='', status=200):
        """Create response with CORS headers"""
        response = Response(data, status=status)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response
    
    @http.route('/exchange_token', type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def exchange_token_options(self, **kwargs):
        """Handle OPTIONS preflight for /exchange_token"""
        return self._make_cors_response()
    
    @http.route('/pos_metadata', type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def pos_metadata_options(self, **kwargs):
        """Handle OPTIONS preflight for /pos_metadata"""
        return self._make_cors_response()


# Simple function-level patching without breaking Odoo internals
def add_cors_headers_to_response(response):
    """Add CORS headers to any response object"""
    if hasattr(response, 'headers'):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
    return response


# Multiple patching strategies for maximum coverage

# 1. Patch the main application at WSGI level
if hasattr(http, 'application') and hasattr(http.application, '__call__'):
    original_app = http.application
    
    def app_with_cors(environ, start_response):
        def cors_start_response(status, headers, exc_info=None):
            # Convert to list and add CORS headers
            headers_list = list(headers) if headers else []
            cors_headers = [
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Headers', 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'),
                ('Access-Control-Allow-Credentials', 'true'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS, DELETE, PATCH'),
            ]
            headers_list.extend(cors_headers)
            return start_response(status, headers_list, exc_info)
        
        return original_app(environ, cors_start_response)
    
    http.application = app_with_cors
    _logger.info('SIMPOS CORS: Patched WSGI application')

# 2. Patch root dispatch if available
if hasattr(http, 'root') and hasattr(http.root, '__call__'):
    original_root_call = http.root.__call__
    
    def root_call_with_cors(self, environ, start_response):
        def cors_start_response(status, headers, exc_info=None):
            headers_list = list(headers) if headers else []
            cors_headers = [
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Headers', 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'),
                ('Access-Control-Allow-Credentials', 'true'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS, DELETE, PATCH'),
            ]
            headers_list.extend(cors_headers)
            return start_response(status, headers_list, exc_info)
        
        return original_root_call(environ, cors_start_response)
    
    http.root.__call__ = root_call_with_cors
    _logger.info('SIMPOS CORS: Patched root __call__')

# 3. Fallback: Patch http.dispatch
if hasattr(http, 'dispatch'):
    original_dispatch = http.dispatch
    
    def dispatch_with_cors(*args, **kwargs):
        try:
            response = original_dispatch(*args, **kwargs)
            return add_cors_headers_to_response(response)
        except Exception:
            return original_dispatch(*args, **kwargs)
    
    http.dispatch = dispatch_with_cors
    _logger.info('SIMPOS CORS: Patched HTTP dispatch as fallback')

# 4. Also add a catch-all route for any unhandled endpoints
@http.route(['/<path:path>'], type='http', auth='none', methods=['OPTIONS'], csrf=False)
def universal_options(path=None, **kwargs):
    """Universal OPTIONS handler"""
    response = Response('')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

# Add the universal handler to the CORSController
CORSController.universal_options = universal_options

_logger.info('SIMPOS CORS: Multi-layer CORS implementation initialized')
