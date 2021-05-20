# -*- coding: utf-8 -*-

import logging
import uuid

from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    def _get_default_access_token(self):
        return str(uuid.uuid4())

    is_validate = fields.Boolean(string='Validate User')
    redirect_url = fields.Char('redirect_url')
    access_token = fields.Char('Security Token', copy=False, default=_get_default_access_token)
    user_role = fields.Selection([('l1', "L1 User"), ('l2', "L2 User")])