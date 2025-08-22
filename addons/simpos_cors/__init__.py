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


# Hook into HTTP dispatch to add CORS headers
if hasattr(http, 'dispatch'):
    original_dispatch = http.dispatch
    
    def dispatch_with_cors(*args, **kwargs):
        """Add CORS headers to all HTTP responses"""
        try:
            response = original_dispatch(*args, **kwargs)
            return add_cors_headers_to_response(response)
        except Exception:
            # If anything fails, just return the original response
            return original_dispatch(*args, **kwargs)
    
    http.dispatch = dispatch_with_cors
    _logger.info('SIMPOS CORS: Successfully patched HTTP dispatch')
else:
    _logger.warning('SIMPOS CORS: Could not find http.dispatch to patch')

_logger.info('SIMPOS CORS: Simple CORS implementation initialized')
