# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import api, fields, models

class WebkulWebsiteAddons(models.TransientModel):
	_inherit = 'webkul.website.addons'

	module_display_price_after_login = fields.Boolean("Display Price After Login")
