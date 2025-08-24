# -*- coding: utf-8 -*-
import logging
from odoo import http, api
from odoo.http import request
from datetime import datetime, timedelta
import jwt


def make_error(message):
    return dict(success=False, error=message)


class AuthTokenController(http.Controller):
    @http.route('/simpos/v1/sign_in', type='http', auth='none', csrf=False, methods=['POST', 'OPTIONS'])
    def get_token(self, **args):
        import logging
        import json
        from werkzeug.wrappers import Response
        
        _logger = logging.getLogger(__name__)
        
        # Handle OPTIONS preflight requests
        if request.httprequest.method == 'OPTIONS':
            response = Response('')
            # Allow multiple origins for development
            origin = request.httprequest.headers.get('Origin', '')
            allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']  # null for file:// protocol
            if origin in allowed_origins or origin.startswith('file://'):
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, x-openerp-session-id, authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE, PATCH'
            _logger.info(f'SIMPOS AUTH: Handled OPTIONS preflight for sign-in from origin: {origin}')
            return response
        
        # Parse JSON data from POST request
        try:
            data = json.loads(request.httprequest.get_data(as_text=True))
            params = data.get('params', {})
            _logger.info(f'Received params: {params}')
        except Exception as e:
            _logger.error(f'Failed to parse JSON data: {e}')
            error_response = json.dumps(make_error('Invalid JSON data'))
            response = Response(error_response, content_type='application/json')
            origin = request.httprequest.headers.get('Origin', '')
            allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
            if origin in allowed_origins or origin.startswith('file://'):
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        # Get database name from request parameters
        db_name = params.get('db') or request.session.db
        _logger.info(f'db_name extracted: {db_name}')
        
        if not db_name:
            error_response = json.dumps(make_error('Database name is required'))
            response = Response(error_response, content_type='application/json')
            origin = request.httprequest.headers.get('Origin', '')
            allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
            if origin in allowed_origins or origin.startswith('file://'):
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        request.session.db = db_name
        _logger.info(f'Set session.db to: {request.session.db}')
        
        # Use Odoo's native password verification
        from odoo import registry, SUPERUSER_ID
        
        try:
            # Get database registry directly (fix deprecation warning)
            from odoo.modules.registry import Registry
            reg = Registry(db_name)
            
            with reg.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                
                # Find user by login
                user = env['res.users'].search([('login', '=', params.get('login'))], limit=1)
                
                if user and user.active:
                    # Properly authenticate user using Odoo's auth mechanism
                    user_id = user.id
                    # Use Odoo's session authentication
                    request.session.authenticate(db_name, params.get('login'), params.get('password'))
                    _logger.info(f'User authenticated with session for user {user_id}')
                else:
                    _logger.info(f'User not found or inactive: {params.get("login")}')
                    user_id = None
                    
        except Exception as e:
            _logger.error(f'Authentication system error: {e}', exc_info=True)
            user_id = None

        if user_id:
            # Session already set above, just proceed with token generation

            user = request.env['res.users'].sudo().browse(user_id)
            user._update_last_login()
            secret_key = request.env['ir.config_parameter'].sudo(
            ).get_param('database.secret')
            token = jwt.encode({
                'uid': user_id,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(days=90)
            }, secret_key, algorithm="HS256")
            response_data = {
                'success': True,
                'data': {
                    'access_token': token,
                    'db_name': db_name,
                    'uid': user_id,
                    "name": user.name,
                    "username": user.login,
                },
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
            _logger.info(f'SIMPOS AUTH: Added CORS headers to successful sign-in response for origin: {origin}')
            return response

        # Return error response with CORS headers
        error_response = json.dumps(make_error('Incorrect login name or password'))
        response = Response(error_response, content_type='application/json')
        origin = request.httprequest.headers.get('Origin', '')
        allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173', 'null']
        if origin in allowed_origins or origin.startswith('file://'):
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        _logger.info(f'SIMPOS AUTH: Added CORS headers to error sign-in response for origin: {origin}')
        return response
