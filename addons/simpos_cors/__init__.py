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


# Enhanced CORS patching - multiple strategies for maximum coverage

# 1. Patch JsonRequest._json_response method
if hasattr(http, 'JsonRequest') and hasattr(http.JsonRequest, '_json_response'):
    original_json_response = http.JsonRequest._json_response
    
    def json_response_with_cors(self, result=None, error=None):
        """Override JsonRequest._json_response to add CORS headers"""
        response = original_json_response(self, result, error)
        
        # Add CORS headers to the response
        if hasattr(response, 'headers'):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
        
        return response
    
    http.JsonRequest._json_response = json_response_with_cors
    _logger.info('SIMPOS CORS: Patched JsonRequest._json_response method')

# 2. Patch JsonRequest.dispatch method as backup
if hasattr(http, 'JsonRequest') and hasattr(http.JsonRequest, 'dispatch'):
    original_json_dispatch = http.JsonRequest.dispatch
    
    def json_dispatch_with_cors(self):
        """Override JsonRequest.dispatch to add CORS headers"""
        response = original_json_dispatch(self)
        
        # Add CORS headers to the response
        if hasattr(response, 'headers'):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
        
        return response
    
    http.JsonRequest.dispatch = json_dispatch_with_cors
    _logger.info('SIMPOS CORS: Patched JsonRequest.dispatch method')

# 3. Patch the main HTTP dispatch function to catch all responses
if hasattr(http, 'dispatch'):
    original_dispatch = http.dispatch
    
    def dispatch_with_cors(request, start_response):
        """Add CORS headers at the WSGI level"""
        def cors_start_response(status, headers, exc_info=None):
            headers_list = list(headers) if headers else []
            
            # Remove existing CORS headers to avoid duplicates
            headers_list = [(k, v) for k, v in headers_list if not k.lower().startswith('access-control')]
            
            # Add CORS headers
            cors_headers = [
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Headers', 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'),
                ('Access-Control-Allow-Credentials', 'true'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS, DELETE, PATCH'),
            ]
            headers_list.extend(cors_headers)
            
            return start_response(status, headers_list, exc_info)
        
        return original_dispatch(request, cors_start_response)
    
    http.dispatch = dispatch_with_cors
    _logger.info('SIMPOS CORS: Patched http.dispatch for WSGI-level CORS')

_logger.info('SIMPOS CORS: Enhanced multi-layer CORS implementation loaded')
