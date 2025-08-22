from odoo import http, api
import logging
import json
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
    
    @http.route('/exchange_token', type='http', auth='none', methods=['OPTIONS', 'POST'], csrf=False)
    def exchange_token(self, **kwargs):
        """Handle /exchange_token authentication endpoint"""
        if http.request.httprequest.method == 'OPTIONS':
            return self._make_cors_response()
        
        # Handle POST request - bridge to actual authentication
        try:
            import json
            from odoo import registry, SUPERUSER_ID
            from odoo.http import request
            
            # Get parameters from request body (axios sends JSON)
            params = {}
            try:
                # Try to get JSON body data
                raw_data = request.httprequest.get_data()
                if raw_data:
                    data = json.loads(raw_data.decode('utf-8'))
                    params = data.get('params', data)  # Handle both nested and flat structures
                else:
                    # Fallback to query params or form data
                    params = dict(request.httprequest.values)
            except:
                # Last fallback - try form/query params
                params = dict(request.httprequest.values)
            
            db_name = params.get('db')
            login = params.get('login')
            password = params.get('password')
            
            # Debug logging
            _logger.info(f'/exchange_token received params: {params}')
            _logger.info(f'db_name: {db_name}, login: {login}, password: {"***" if password else None}')
            _logger.info(f'Raw request data: {request.httprequest.get_data()}')
            
            if not all([db_name, login, password]):
                response = self._make_cors_response(
                    json.dumps({
                        'error': 'Missing required parameters: db, login, password',
                        'received_params': list(params.keys()) if params else []
                    }),
                    400
                )
                response.headers['Content-Type'] = 'application/json'
                return response
            
            # Simple authentication like in simpos_token_authentication
            # First check current session database
            _logger.info(f'Current session.db before: {getattr(request.session, "db", None)}')
            
            # Set database and authenticate exactly like the working controller
            request.session.db = db_name
            _logger.info(f'Set session.db to: {request.session.db}')
            
            # Try different authenticate signatures since Odoo 18 changed
            try:
                # Try with db_name first (like token auth controller)
                user_id = request.session.authenticate(db_name, login, password)
            except TypeError as te:
                _logger.info(f'First authenticate method failed: {te}, trying without db_name')
                # Try without db_name if that fails
                user_id = request.session.authenticate(login, password)
            
            _logger.info(f'Authentication result: user_id={user_id}')
            
            if user_id:
                request.session.uid = user_id
                request.session.login = login
                # Success - return session info similar to /simpos/v1/sign_in
                # Get user info using request.env (like in token auth)
                user = request.env['res.users'].sudo().browse(user_id)
                user._update_last_login()
                
                result = {
                    'uid': user_id,
                    'session_id': request.session.sid,
                    'user_context': request.session.context,
                    'username': user.name,
                    'login': user.login,
                    'db_name': db_name,
                }
                    
                response = self._make_cors_response(json.dumps(result))
                response.headers['Content-Type'] = 'application/json'
                return response
            else:
                # Authentication failed
                response = self._make_cors_response(
                    json.dumps({'error': 'Invalid credentials'}),
                    401
                )
                response.headers['Content-Type'] = 'application/json'
                return response
                
        except Exception as e:
            _logger.error(f'Error in /exchange_token: {str(e)}', exc_info=True)
            response = self._make_cors_response(
                json.dumps({'error': 'Authentication error'}),
                500
            )
            response.headers['Content-Type'] = 'application/json'
            return response
    
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


# Multiple patching strategies for maximum coverage

# 1. Patch the main application at WSGI level
if hasattr(http, 'application') and hasattr(http.application, '__call__'):
    original_app = http.application
    
    def app_with_cors(environ, start_response):
        def cors_start_response(status, headers, exc_info=None):
            # Convert to list and add CORS headers
            headers_list = list(headers) if headers else []
            cors_headers = [
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Headers', 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'),
                ('Access-Control-Allow-Credentials', 'true'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS, DELETE, PATCH'),
            ]
            headers_list.extend(cors_headers)
            return start_response(status, headers_list, exc_info)
        
        return original_app(environ, cors_start_response)
    
    http.application = app_with_cors
    _logger.info('SIMPOS CORS: Patched WSGI application')

# 2. Patch root dispatch if available
if hasattr(http, 'root') and hasattr(http.root, '__call__'):
    original_root_call = http.root.__call__
    
    def root_call_with_cors(self, environ, start_response):
        def cors_start_response(status, headers, exc_info=None):
            headers_list = list(headers) if headers else []
            cors_headers = [
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Headers', 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'),
                ('Access-Control-Allow-Credentials', 'true'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS, DELETE, PATCH'),
            ]
            headers_list.extend(cors_headers)
            return start_response(status, headers_list, exc_info)
        
        return original_root_call(environ, cors_start_response)
    
    http.root.__call__ = root_call_with_cors
    _logger.info('SIMPOS CORS: Patched root __call__')

# 3. Fallback: Patch http.dispatch
if hasattr(http, 'dispatch'):
    original_dispatch = http.dispatch
    
    def dispatch_with_cors(*args, **kwargs):
        try:
            response = original_dispatch(*args, **kwargs)
            return add_cors_headers_to_response(response)
        except Exception:
            return original_dispatch(*args, **kwargs)
    
    http.dispatch = dispatch_with_cors
    _logger.info('SIMPOS CORS: Patched HTTP dispatch as fallback')

# 4. Also add a catch-all route for any unhandled endpoints
@http.route(['/<path:path>'], type='http', auth='none', methods=['OPTIONS'], csrf=False)
def universal_options(path=None, **kwargs):
    """Universal OPTIONS handler"""
    response = Response('')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

# Add the universal handler to the CORSController
CORSController.universal_options = universal_options

_logger.info('SIMPOS CORS: Multi-layer CORS implementation initialized')
