# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import api,exceptions,fields,models


class PriceConfigSettings(models.Model):
	_name = 'price.config.settings'
	_description = 'Price Visibility Configuration'

	def _default_website(self):
		return self.env['website'].search([], limit=1)

	name       = fields.Char('Name',required=True)
	is_active  = fields.Boolean('Active on website',default=False,copy=False)
	website_id = fields.Many2one(
		comodel_name = 'website',
		string       = 'Website',
		default      = _default_website,
		required     = True
	)
	global_price_visibility = fields.Selection(
		selection=[
			('show','Show Price'),
			('login','Login For Price'),
			('contact','Contact For Price')
		],
		string   = 'Global Price Visibility',
		required = True
	)

	@api.model
	def create(self, vals):
		if vals.get('is_active'):
			self.search(
				[
					('website_id','=',vals.get('website_id',self._default_website().id)),
					('is_active','=',True),
				]
			).write({'is_active':False})
		return super(PriceConfigSettings, self).create(vals)

	def toggle_is_active(self):
		self.ensure_one()
		if not self.is_active:
			self.search(
				[('website_id','=',self.website_id.id),('is_active','=',True)]
			).write({'is_active':False})
		self.is_active = not self.is_active
