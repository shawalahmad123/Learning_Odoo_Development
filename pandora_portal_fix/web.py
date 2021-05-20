# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.addons.portal.controllers.web import Home

class CustomPortal(Home):
    
    
    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        return super(Home, self).web_client(s_action, **kw)

     