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
    
    @http.route(['/web/session/authenticate', '/web/session/modules', '/web/session/get_session_info'], 
                type='json', auth='none', methods=['POST', 'OPTIONS'], cors='*')
    def session_cors(self, **kwargs):
        """Add CORS to session endpoints"""
        if http.request.httprequest.method == 'OPTIONS':
            return self._cors_preflight_response()
        # Let the original handler process the request
        return None


# Modern Odoo 18 approach: Use dispatch_rpc hook
original_dispatch_rpc = http.dispatch_rpc

def dispatch_rpc_with_cors(service_name, method, params):
    """Add CORS headers to all RPC responses"""
    response = original_dispatch_rpc(service_name, method, params)
    
    if hasattr(http.request, 'httprequest'):
        # Add CORS headers to response
        if hasattr(response, 'headers'):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE'
    
    return response

# Apply the CORS wrapper
http.dispatch_rpc = dispatch_rpc_with_cors

_logger.info('SIMPOS CORS: Modern CORS middleware initialized for Odoo 18')
