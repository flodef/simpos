from odoo import http
import logging
from werkzeug.wrappers import Response

_logger = logging.getLogger(__name__)


class CORSController(http.Controller):
    """CORS controller for API endpoints"""
    
    @http.route('/pos_metadata', type='http', auth='none', csrf=False, methods=['OPTIONS'])
    def pos_metadata_options(self, **args):
        """Handle OPTIONS preflight for /pos_metadata"""
        from werkzeug.wrappers import Response
        from odoo.http import request
        
        response = Response('', status=200)
        self._add_cors_headers(response, request.httprequest.headers.get('Origin', ''))
        _logger.info('POS Metadata: OPTIONS preflight handled')
        return response
    
    @http.route('/pos_metadata', type='http', auth='user', csrf=False, methods=['POST'])
    def pos_metadata_post(self, **args):
        """Handle POST for /pos_metadata with Odoo native auth"""
        import json
        from werkzeug.wrappers import Response
        from odoo.http import request
        
        # With auth='user', session is automatically validated
        _logger.info(f'POS Metadata: Session authenticated - uid: {request.session.uid}, db: {request.session.db}')
        
        # Parse JSON data from POST request
        try:
            data = json.loads(request.httprequest.get_data(as_text=True))
            params = data.get('params', {})
            config_id = params.get('config_id')
            _logger.info(f'POS Metadata requested for config_id: {config_id}')
        except Exception as e:
            _logger.error(f'Failed to parse JSON data: {e}')
            return self._cors_error_response('Invalid JSON data')
        
        try:
            # Get current user and company using session context
            user = request.env.user
            company = user.company_id
            _logger.info(f'POS Metadata: Found user {user.name} (ID: {user.id}) from session')
            
            # Build response data (same as before)
            response_data = {
                'success': True,
                'sessionInfo': {
                    'userContext': {
                        'uid': user.id,
                        'user_id': user.id,
                        'name': user.name,
                        'company_id': company.id,
                        'company_name': company.name,
                        'lang': user.lang or 'en_US',
                        'tz': user.tz or 'UTC',
                        'is_admin': user.has_group('base.group_system'),
                        'pos_config_id': config_id if config_id else None,
                    }
                }
            }
            
            # Return JSON response with CORS headers
            json_response = json.dumps(response_data)
            response = Response(json_response, content_type='application/json')
            self._add_cors_headers(response, request.httprequest.headers.get('Origin', ''))
            _logger.info(f'SIMPOS CORS: Returned POS metadata with CORS headers')
            return response
            
        except Exception as e:
            _logger.error(f'Error getting POS metadata: {e}', exc_info=True)
            return self._cors_error_response('Failed to get POS metadata')
    
    @http.route('/pos_metadata', type='http', auth='none', csrf=False, methods=['OPTIONS'])
    def pos_metadata_options(self, **args):
        """Handle OPTIONS preflight for /pos_metadata"""
        from werkzeug.wrappers import Response
        from odoo.http import request
        
        response = Response('', status=200)
        origin = request.httprequest.headers.get('Origin', '')
        self._add_cors_headers(response, origin)
        _logger.info(f'SIMPOS CORS: Handled OPTIONS preflight for /pos_metadata from origin: {origin}')
        return response
    
    def _add_cors_headers(self, response, origin):
        """Add CORS headers to response"""
        allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
        if origin in allowed_origins or origin.startswith('file://'):
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Max-Age'] = '86400'
    
    def _cors_error_response(self, message, status=400):
        """Create error response with CORS headers"""
        import json
        from werkzeug.wrappers import Response
        from odoo.http import request
        
        error_response = json.dumps({'error': message})
        response = Response(error_response, status=status, content_type='application/json')
        self._add_cors_headers(response, request.httprequest.headers.get('Origin', ''))
        return response
    
    @http.route('/web/dataset/call_kw/<path:path>', type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def web_dataset_options(self, path=None, **kwargs):
        """Handle OPTIONS preflight for /web/dataset/call_kw/* endpoints"""
        from odoo.http import request
        response = Response('')
        origin = request.httprequest.headers.get('Origin', '')
        allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
        if origin in allowed_origins or origin.startswith('file://'):
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
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
        
        # Add CORS headers for cross-origin requests
        from odoo.http import request
        if hasattr(request, 'httprequest') and request.httprequest:
            origin = request.httprequest.headers.get('Origin', '')
            if origin and origin != request.httprequest.host_url.rstrip('/'):
                allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
                if origin in allowed_origins or origin.startswith('file://'):
                    self.headers['Access-Control-Allow-Origin'] = origin
                else:
                    self.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
                self.headers['Access-Control-Allow-Credentials'] = 'true'
                self.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
                self.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
                _logger.debug(f'SIMPOS CORS: Added CORS headers to Werkzeug response for origin: {origin}')
    
    WerkzeugResponse.__init__ = werkzeug_init_with_cors
    _logger.info('SIMPOS CORS: Patched Werkzeug Response.__init__')

# Patch http.JsonRequest._json_response more aggressively
if hasattr(http, 'JsonRequest'):
    original_json_response = getattr(http.JsonRequest, '_json_response', None)
    
    if original_json_response:
        def patched_json_response(self, result=None, error=None):
            _logger.debug(f'SIMPOS CORS: Intercepting JSON response')
            response = original_json_response(self, result, error)
            
            # Add CORS headers for cross-origin requests
            origin = self.httprequest.headers.get('Origin', '')
            if origin and origin != self.httprequest.host_url.rstrip('/'):
                allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
                if origin in allowed_origins or origin.startswith('file://'):
                    response.headers['Access-Control-Allow-Origin'] = origin
                else:
                    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
                _logger.debug(f'SIMPOS CORS: Added CORS headers to JSON response for origin: {origin}')
            
            return response
        
        http.JsonRequest._json_response = patched_json_response
        _logger.info('SIMPOS CORS: Aggressively patched JsonRequest._json_response')

# Additional patch for JSON route dispatch
if hasattr(http, 'JsonRequest') and hasattr(http.JsonRequest, 'dispatch'):
    original_json_dispatch = http.JsonRequest.dispatch
    
    def patched_json_dispatch(self):
        route_path = getattr(self.httprequest, "path", "unknown")
        _logger.info(f'SIMPOS CORS: JSON dispatch called for route: {route_path}')
        response = original_json_dispatch(self)
        
        # Add CORS headers for cross-origin requests to standard Odoo endpoints
        origin = self.httprequest.headers.get('Origin', '')
        if origin and origin != self.httprequest.host_url.rstrip('/') and hasattr(response, 'headers'):
            allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
            if origin in allowed_origins or origin.startswith('file://'):
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
            _logger.debug(f'SIMPOS CORS: Added CORS headers to JSON dispatch response for {route_path} from origin: {origin}')
        
        return response
    
    http.JsonRequest.dispatch = patched_json_dispatch
    _logger.info('SIMPOS CORS: Patched JsonRequest.dispatch for JSON routes')

_logger.info('SIMPOS CORS: Multi-level response patching implementation loaded')
