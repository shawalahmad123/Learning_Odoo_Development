# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.http_routing.models.ir_http import slug


class WebsiteSale(WebsiteSale):
	@http.route(['/shop/cart/update'], type='http', auth="public", methods=['GET', 'POST'], website=True, csrf=False)
	def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
		template = request.env['product.product'].sudo().browse(int(product_id)).product_tmpl_id
		price_visibility = template.get_price_visibility(request.website.id)

		if price_visibility == 'contact':
			company = request.env['res.company'].sudo()._company_default_get('display_price_after_login')
			return http.local_redirect('mailto:%s?subject=Price for %s'%(company.email,template.name))

		elif price_visibility == 'login' and request.env.user == request.website.user_id:
			return http.local_redirect('/web/login?redirect=/shop/product/%s'%slug(template))

		return super(WebsiteSale, self).cart_update(product_id, add_qty, set_qty, **kw)

	def _get_products_recently_viewed(self):
		"""
		Returns list of recently viewed products according to current user
		"""
		max_number_of_product_for_carousel = 12
		visitor = request.env['website.visitor']._get_visitor_from_request()
		if visitor:
			excluded_products = request.website.sale_get_order().mapped('order_line.product_id.id')
			products = request.env['website.track'].sudo().read_group(
				[
					('visitor_id', '=', visitor.id),
					('product_id', '!=', False),
					('product_id', 'not in', excluded_products)
				],
				['product_id', 'visit_datetime:max'],
				['product_id'],
				limit=max_number_of_product_for_carousel,
				orderby='visit_datetime DESC'
			)
			products_ids = [product['product_id'][0] for product in products]
			if products_ids:
				viewed_products = request.env['product.product'].browse(products_ids)

				FieldMonetary = request.env['ir.qweb.field.monetary']
				monetary_options = {
					'display_currency': request.website.get_current_pricelist().currency_id,
				}
				rating = request.website.viewref('website_sale.product_comment').active
				res = {'products': []}
				for product in viewed_products:
					price_visibility = product.product_tmpl_id.get_price_visibility(request.website.id)
					if price_visibility == 'contact' or \
						price_visibility == 'login' and \
						request.env.user == request.website.user_id:
						continue
					combination_info = product._get_combination_info_variant()
					res_product = product.read(['id', 'name', 'website_url'])[0]
					res_product.update(combination_info)
					res_product['price'] = FieldMonetary.value_to_html(res_product['price'], monetary_options)
					if rating:
						res_product['rating'] = request.env["ir.ui.view"].render_template(
							'website_rating.rating_widget_stars_static',
							values={
								'rating_avg': product.rating_avg,
								'rating_count': product.rating_count,
							}
						)
					res['products'].append(res_product)
				return res
		return {}
