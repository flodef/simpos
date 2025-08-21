from odoo import http
from odoo.tools import config
import logging

_logger = logging.getLogger(__name__)


class CORSController(http.Controller):
    """Add CORS headers to API responses"""
    
    def _cors_preflight_response(self):
        """Handle CORS preflight OPTIONS requests"""
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS, DELETE',
            'Access-Control-Max-Age': '86400',
        }
        return http.request.make_response('', headers=headers)
    
    @http.route('/exchange_token', type='http', auth='none', methods=['POST', 'OPTIONS'], cors='*', csrf=False)
    def exchange_token_cors(self, **kwargs):
        """Handle CORS for /exchange_token endpoint"""
        if http.request.httprequest.method == 'OPTIONS':
            return self._cors_preflight_response()
        # Let the original handler process the request by returning None
        return None
    
    @http.route('/pos_metadata', type='http', auth='none', methods=['POST', 'OPTIONS'], cors='*', csrf=False)
    def pos_metadata_cors(self, **kwargs):
        """Handle CORS for /pos_metadata endpoint"""
        if http.request.httprequest.method == 'OPTIONS':
            return self._cors_preflight_response()
        return None


# Hook into Odoo's response processing to add CORS headers
original_make_response = http.request.make_response if hasattr(http, 'request') else None

def make_response_with_cors(*args, **kwargs):
    """Add CORS headers to all responses"""
    if hasattr(http.request, 'make_response'):
        response = http.request.make_response(*args, **kwargs)
    else:
        # Fallback for cases where make_response isn't available
        from werkzeug.wrappers import Response
        response = Response(*args, **kwargs)
    
    # Add CORS headers to all responses
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE'
    
    return response

# Monkey patch the response creation (this approach works better for custom endpoints)
try:
    if hasattr(http.request, 'make_response'):
        http.request.make_response = make_response_with_cors
except AttributeError:
    # Request object not available during module load, will be patched at runtime
    pass

# Runtime patching when request is available
original_dispatch = http.dispatch

def dispatch_with_cors(*args, **kwargs):
    """Dispatch with CORS header injection"""
    response = original_dispatch(*args, **kwargs)
    
    # Add CORS headers to response
    if hasattr(response, 'headers'):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE'
    
    return response

# Apply the CORS wrapper to the main dispatch function
http.dispatch = dispatch_with_cors

_logger.info('SIMPOS CORS: Modern CORS middleware initialized for Odoo 18')
