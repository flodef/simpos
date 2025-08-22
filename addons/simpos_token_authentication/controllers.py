# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import jwt


def make_error(message):
    return dict(success=False, error=message)


class AuthTokenController(http.Controller):
    @http.route('/simpos/v1/sign_in', type='json', auth='none')
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
        
        # Use the correct Odoo 18 authenticate signature
        try:
            user_id = request.session.authenticate(db_name, args.get('login'), args.get('password'))
            _logger.info(f'authenticate(db, login, pass) succeeded: {user_id}')
        except TypeError as e:
            _logger.info(f'3-param authenticate failed: {e}, trying 2-param')
            # Some Odoo 18 versions use 2 params after setting session.db
            user_id = request.session.authenticate(args.get('login'), args.get('password'))
            _logger.info(f'authenticate(login, pass) result: {user_id}')

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
            return {
                'success': True,
                'data': {
                    'access_token': token,
                    'db_name': db_name,
                    'uid': user_id,
                    "name": user.name,
                    "username": user.login,
                },
            }

        return make_error('Incorrect login name or password')
