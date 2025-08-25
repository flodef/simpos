from odoo import http
import logging
from werkzeug.wrappers import Response

_logger = logging.getLogger(__name__)


class CORSController(http.Controller):
    """CORS controller for API endpoints"""
    
    @http.route('/pos_metadata', type='http', auth='none', csrf=False, methods=['OPTIONS', 'POST'], save_session=False)
    def pos_metadata_handler(self, **args):
        """Handle both OPTIONS and POST for /pos_metadata with CORS support"""
        import json
        from werkzeug.wrappers import Response
        from odoo.http import request
        
        # Handle OPTIONS preflight requests
        if request.httprequest.method == 'OPTIONS':
            response = Response('', status=200)
            origin = request.httprequest.headers.get('Origin', '')
            allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
            if origin in allowed_origins or origin.startswith('file://'):
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
            response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response.headers['Access-Control-Max-Age'] = '86400'
            _logger.info(f'SIMPOS CORS: Handled OPTIONS preflight for /pos_metadata from origin: {origin}')
            return response
        
        # Verify user authentication for POST requests
        if not request.session.uid:
            error_response = json.dumps({'error': 'Authentication required'})
            response = Response(error_response, status=401, content_type='application/json')
            origin = request.httprequest.headers.get('Origin', '')
            allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
            if origin in allowed_origins or origin.startswith('file://'):
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        # Parse JSON data from POST request
        try:
            data = json.loads(request.httprequest.get_data(as_text=True))
            params = data.get('params', {})
            config_id = params.get('config_id')
            _logger.info(f'POS Metadata requested for config_id: {config_id}')
        except Exception as e:
            _logger.error(f'Failed to parse JSON data: {e}')
            error_response = json.dumps({'error': 'Invalid JSON data'})
            response = Response(error_response, content_type='application/json')
            origin = request.httprequest.headers.get('Origin', '')
            allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
            if origin in allowed_origins or origin.startswith('file://'):
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        try:
            # Get user from current session (should be authenticated from sign-in)
            _logger.info(f'Checking session: uid={request.session.uid}, db={request.session.db}, login={request.session.login}')
            if not request.session.uid:
                _logger.error('No authenticated user session found')
                error_response = json.dumps({'error': 'Not authenticated'})
                response = Response(error_response, content_type='application/json', status=401)
                origin = request.httprequest.headers.get('Origin', '')
                allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
                if origin in allowed_origins or origin.startswith('file://'):
                    response.headers['Access-Control-Allow-Origin'] = origin
                else:
                    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                return response
            
            # Get current user session info
            user = request.env.user
            company = user.company_id
            
            # Build response data similar to standard Odoo POS metadata
            response_data = {
                'loginNumber': 1,
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
            origin = request.httprequest.headers.get('Origin', '')
            allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
            if origin in allowed_origins or origin.startswith('file://'):
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
            _logger.info(f'SIMPOS CORS: Returned POS metadata with CORS headers for origin: {origin}')
            return response
            
        except Exception as e:
            _logger.error(f'Error getting POS metadata: {e}', exc_info=True)
            error_response = json.dumps({'error': 'Failed to get POS metadata'})
            response = Response(error_response, content_type='application/json')
            origin = request.httprequest.headers.get('Origin', '')
            allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
            if origin in allowed_origins or origin.startswith('file://'):
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
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
