# -*- coding: utf-8 -*-

from odoo import models, fields, api, http
from odoo.exceptions import AccessDenied
from odoo.http import request
import jwt


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _auth_method_user(cls):
        token = request.httprequest.headers.get('Authorization')
        if token:
            token = token.replace('Bearer ', '')
            payload = jwt.decode(token, request.env['ir.config_parameter'].sudo().get_param('database.secret'), algorithms=["HS256"])
            # Use update_env instead of direct uid assignment (Odoo 18 compatibility)
            request.update_env(user=payload.get('uid'))
        else:
            super(IrHttp, cls)._auth_method_user()
