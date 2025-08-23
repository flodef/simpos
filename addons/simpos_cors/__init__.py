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


# Patch Werkzeug Response class directly
from werkzeug.wrappers import Response as WerkzeugResponse

if hasattr(WerkzeugResponse, '__init__'):
    original_werkzeug_init = WerkzeugResponse.__init__
    
    def werkzeug_init_with_cors(self, *args, **kwargs):
        # Call original init
        original_werkzeug_init(self, *args, **kwargs)
        
        # Add CORS headers to ALL Werkzeug responses
        self.headers['Access-Control-Allow-Origin'] = '*'
        self.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
        self.headers['Access-Control-Allow-Credentials'] = 'true'
        self.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
        
        _logger.debug(f'SIMPOS CORS: Added CORS headers to Werkzeug response')
    
    WerkzeugResponse.__init__ = werkzeug_init_with_cors
    _logger.info('SIMPOS CORS: Patched Werkzeug Response.__init__')

# Alternative: Patch http.JsonRequest._json_response more aggressively
if hasattr(http, 'JsonRequest'):
    original_json_response = getattr(http.JsonRequest, '_json_response', None)
    
    if original_json_response:
        def patched_json_response(self, result=None, error=None):
            _logger.debug(f'SIMPOS CORS: Intercepting JSON response')
            response = original_json_response(self, result, error)
            
            # Force add CORS headers
            if hasattr(response, 'headers'):
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
                _logger.debug(f'SIMPOS CORS: Added CORS headers to JSON response: {response.headers}')
            
            return response
        
        http.JsonRequest._json_response = patched_json_response
        _logger.info('SIMPOS CORS: Aggressively patched JsonRequest._json_response')

_logger.info('SIMPOS CORS: Multi-level response patching implementation loaded')
