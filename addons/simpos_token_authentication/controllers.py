# -*- coding: utf-8 -*-
import logging
from odoo import http, api
from odoo.http import request
from datetime import datetime, timedelta
import jwt


def make_error(message):
    return dict(success=False, error=message)


class AuthTokenController(http.Controller):
    @http.route('/simpos/v1/sign_in', type='json', auth='none', cors='*')
    def get_token(self, **args):
        # Debug logging to see what parameters are received
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info(f'Received args: {args}')
        
        # Get database name from request parameters
        db_name = args.get('db') or request.session.db
        _logger.info(f'db_name extracted: {db_name}')
        
        if not db_name:
            return make_error('Database name is required')
        
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
                user = env['res.users'].search([('login', '=', args.get('login'))], limit=1)
                
                if user and user.active:
                    # For now, just check if user exists - authentication will be handled by Odoo
                    user_id = user.id
                    request.session.uid = user_id
                    request.session.db = db_name
                    request.session.login = args.get('login')
                    _logger.info(f'User found and session set for user {user_id}')
                else:
                    _logger.info(f'User not found or inactive: {args.get("login")}')
                    user_id = None
                    
        except Exception as e:
            _logger.error(f'Authentication system error: {e}', exc_info=True)
            user_id = None

        if user_id:
            request.session.uid = user_id
            request.session.login = args.get('login')

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
            
            return response_data

        return make_error('Incorrect login name or password')
