# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import api,fields,models


class PriceVisibilityUpdate(models.TransientModel):
	_name = 'price.visibility.update'
	_description = 'Update Price Visibility'

	price_visibility = fields.Selection(
		selection=[
			('show','Show Price'),
			('login','Login to view Price'),
			('contact','Contact For Price'),
			('','None'),
		],
		string='Price Visibility',
		default='',
	)

	def updateVisibility(self):
		self.env['product.template'].browse(
			self.env.context.get('active_ids')
		).write({'price_visibility': self.price_visibility})
