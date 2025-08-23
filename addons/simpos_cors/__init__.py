from odoo import http
import logging
from werkzeug.wrappers import Response

_logger = logging.getLogger(__name__)


class CORSController(http.Controller):
    """CORS controller for API endpoints"""
    
    @http.route('/simpos/v1/sign_in', type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def simpos_sign_in_options(self, **kwargs):
        """Handle OPTIONS preflight for /simpos/v1/sign_in"""
        response = Response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response
    
    @http.route('/web/dataset/call_kw/<path:path>', type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def web_dataset_options(self, path=None, **kwargs):
        """Handle OPTIONS preflight for /web/dataset/call_kw/* endpoints"""
        response = Response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response


# Direct WSGI middleware approach - intercept all responses
def cors_wsgi_middleware(app):
    """WSGI middleware that adds CORS headers to all responses"""
    def cors_application(environ, start_response):
        def cors_start_response(status, headers, exc_info=None):
            # Convert headers to list if it's not already
            headers_list = list(headers) if headers else []
            
            # Remove existing CORS headers to avoid duplicates
            headers_list = [(k, v) for k, v in headers_list 
                           if not k.lower().startswith('access-control')]
            
            # Add CORS headers to ALL responses
            cors_headers = [
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Headers', 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'),
                ('Access-Control-Allow-Credentials', 'true'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS, DELETE, PATCH'),
            ]
            headers_list.extend(cors_headers)
            
            return start_response(status, headers_list, exc_info)
        
        return app(environ, cors_start_response)
    
    return cors_application

# Apply WSGI middleware to Odoo application
if hasattr(http, 'root') and hasattr(http.root, 'dispatch'):
    # Wrap the entire Odoo WSGI application
    original_root = http.root
    
    class CORSRoot:
        def __init__(self, original):
            self.original = original
            
        def __call__(self, environ, start_response):
            return cors_wsgi_middleware(self.original)(environ, start_response)
        
        def __getattr__(self, name):
            return getattr(self.original, name)
    
    http.root = CORSRoot(original_root)
    _logger.info('SIMPOS CORS: Applied WSGI middleware to Odoo root application')

_logger.info('SIMPOS CORS: Direct WSGI middleware CORS implementation loaded')
