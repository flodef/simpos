from odoo import http
from odoo.tools import config
from odoo.service import wsgi_server
import logging
from werkzeug.wrappers import Response

_logger = logging.getLogger(__name__)


class CORSMiddleware(object):
    """WSGI middleware to add CORS headers to all responses"""
    
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def cors_start_response(status, headers, exc_info=None):
            """Add CORS headers to every response"""
            cors_headers = [
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Headers', 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'),
                ('Access-Control-Allow-Credentials', 'true'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS, DELETE, PATCH'),
                ('Access-Control-Max-Age', '86400'),
            ]
            
            # Convert headers to list and add CORS headers
            headers_list = list(headers)
            headers_list.extend(cors_headers)
            
            return start_response(status, headers_list, exc_info)
        
        # Handle preflight OPTIONS requests
        if environ.get('REQUEST_METHOD') == 'OPTIONS':
            response = Response('')
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
            response.headers['Access-Control-Max-Age'] = '86400'
            return response(environ, start_response)
        
        return self.app(environ, cors_start_response)


# Patch Odoo's WSGI application with CORS middleware
def patch_wsgi_server():
    """Patch the WSGI server to include CORS middleware"""
    try:
        # Get the original application
        if hasattr(wsgi_server, 'application'):
            original_app = wsgi_server.application
            # Wrap it with CORS middleware
            wsgi_server.application = CORSMiddleware(original_app)
            _logger.info('SIMPOS CORS: Successfully patched WSGI server with CORS middleware')
            return True
    except Exception as e:
        _logger.error(f'SIMPOS CORS: Failed to patch WSGI server: {e}')
    
    return False


# Alternative approach: Patch HTTP root
def patch_http_root():
    """Patch HTTP root application"""
    try:
        if hasattr(http, 'root') and hasattr(http.root, 'dispatch'):
            original_app = http.root.dispatch
            http.root.dispatch = CORSMiddleware(original_app)
            _logger.info('SIMPOS CORS: Successfully patched HTTP root with CORS middleware')
            return True
    except Exception as e:
        _logger.error(f'SIMPOS CORS: Failed to patch HTTP root: {e}')
    
    return False


# Apply CORS patches
patch_success = patch_wsgi_server() or patch_http_root()

if not patch_success:
    _logger.warning('SIMPOS CORS: Could not apply WSGI middleware, falling back to response patching')
    
    # Fallback: Patch individual responses
    original_make_response = None
    if hasattr(http.request, 'make_response'):
        original_make_response = http.request.make_response
    
    def make_response_with_cors(data, headers=None, cookies=None, status=200):
        """Add CORS headers to responses"""
        if original_make_response:
            response = original_make_response(data, headers, cookies, status)
        else:
            response = Response(data, status=status, headers=headers)
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE'
        
        return response
    
    # Try to patch make_response
    try:
        if hasattr(http, 'request'):
            http.request.make_response = make_response_with_cors
    except:
        pass

_logger.info('SIMPOS CORS: Odoo 18 CORS middleware initialization complete')
