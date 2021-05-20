# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import api,fields,models


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	price_visibility = fields.Selection(
		selection=[
			('show','Show Price'),
			('login','Login to view Price'),
			('contact','Contact For Price'),
			('',''),
		],
		string='Price Visibility',
		default='',
	)

	def get_price_visibility(self, website_id):
		self.ensure_one()
		if self.price_visibility:
			return self.price_visibility
		else:
			return self.env['price.config.settings'].sudo().search(
				[
					('website_id','=',website_id),
					('is_active','=',True)
				],
			).global_price_visibility
		return 'show'
