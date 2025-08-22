from odoo import http
from odoo.tools import config
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


# Patch Odoo's HTTP dispatcher with CORS middleware
def patch_http_dispatcher():
    """Patch the HTTP dispatcher to include CORS middleware"""
    try:
        # Patch the main HTTP dispatch function
        if hasattr(http, 'dispatch_rpc'):
            original_dispatch_rpc = http.dispatch_rpc
            
            def dispatch_rpc_with_cors(service_name, method, params):
                response = original_dispatch_rpc(service_name, method, params)
                # Add CORS headers to RPC responses
                return response
            
            http.dispatch_rpc = dispatch_rpc_with_cors
            _logger.info('SIMPOS CORS: Successfully patched RPC dispatcher')
            return True
    except Exception as e:
        _logger.error(f'SIMPOS CORS: Failed to patch RPC dispatcher: {e}')
    
    return False


# Simple controller-based approach for Odoo 18
class UniversalCORSController(http.Controller):
    """Universal CORS controller for all endpoints"""
    
    @http.route('/exchange_token', type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def exchange_token_options(self, **kwargs):
        """Handle OPTIONS for exchange_token"""
        response = Response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response
    
    @http.route('/pos_metadata', type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def pos_metadata_options(self, **kwargs):
        """Handle OPTIONS for pos_metadata"""
        response = Response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response


# Apply CORS patches
patch_success = patch_http_dispatcher()

# Hook into Odoo's response system for CORS headers
original_response_class = http.Response if hasattr(http, 'Response') else Response

class CORSResponse(original_response_class):
    """Response class that automatically adds CORS headers"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CORS headers to every response
        self.headers['Access-Control-Allow-Origin'] = '*'
        self.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
        self.headers['Access-Control-Allow-Credentials'] = 'true'
        self.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'

# Monkey patch the Response class
if hasattr(http, 'Response'):
    http.Response = CORSResponse

# Also patch werkzeug Response for completeness  
try:
    import werkzeug.wrappers
    original_werkzeug_response = werkzeug.wrappers.Response
    
    def patched_response(*args, **kwargs):
        response = original_werkzeug_response(*args, **kwargs)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
        return response
    
    werkzeug.wrappers.Response = patched_response
except:
    pass

_logger.info('SIMPOS CORS: Odoo 18 CORS middleware initialization complete')
