# -*- coding: utf-8 -*-

import json
import odoo
import werkzeug.urls
import werkzeug.utils
from odoo.http import request
from odoo.tools import image_process
from odoo import api, fields, models, http, tools, _
from odoo.addons.website_sale_wishlist.controllers.main import WebsiteSaleWishlist
from odoo.addons.auth_oauth.controllers.main import OAuthLogin


class Website(models.Model):
    _inherit = "website"

    facebook_sharing = fields.Boolean(string='Facebook')
    twitter_sharing = fields.Boolean(string='Twitter')
    linkedin_sharing = fields.Boolean(string='Linkedin')
    mail_sharing = fields.Boolean(string='Mail')
    is_load_more = fields.Boolean(string='Load More', help="Load moer will be enabled", readonly=False)
    load_more_image = fields.Binary('Load More Image', help="Display this image while load more applies.",
                                    readonly=False)
    button_or_scroll = fields.Selection([
        ('automatic', 'Automatic- on page scroll'),
        ('button', 'Button- on click button')
    ], string="Loading type for products",
        required=True, default='automatic', readonly=False)
    prev_button_label = fields.Char(string='Label for the Prev Button', required=True, readonly=False,
                                    default="Load prev", translate=True)
    next_button_label = fields.Char(string='Label for the Next Button', required=True, readonly=False,
                                    default="Load next", translate=True)
    is_lazy_load = fields.Boolean(string='Lazyload', help="Lazy load will be enabled", readonly=False)
    lazy_load_image = fields.Binary('Lazyload Image', help="Display this image while lazy load applies.",
                                    readonly=False)
    banner_video_url = fields.Char(string='Video URL', help='URL of a video for banner.', readonly=False)
    number_of_product_line = fields.Selection([
        ('1', 1),
        ('2', 2),
        ('3', 3)
    ], string="Number of lines for product name", required=True, default='1', readonly=False, help="Number of lines to show in product name for shop.")


    # @api.depends('banner_video_url')
    # def _compute_embed_code(self):
    #     for image in self:
    #         image.embed_code = get_video_embed_code(image.video_url)

    def getDatabase(self):
        """
                To display database in login popup
                :return: List of databases
                """
        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        return values['databases']

    def category_check(self):
        """
        To display main parent product.public.category website specific
        :return:
        """
        return self.env['product.public.category'].sudo().search(
            [('parent_id', '=', False), ('website_id', 'in', (False, self.id))])

    def get_default_company_address(self):
        """
        To get company default address
        :return:
        """
        street = ''
        street2 = ''
        city = ''
        zip = ''
        state = ''
        country = ''

        getCurrentCompany = request.env['website'].get_current_website().company_id

        values = {
            'street': getCurrentCompany.street,
            'street2': getCurrentCompany.street2,
            'city': getCurrentCompany.city,
            'zip': getCurrentCompany.zip,
            'state_id': getCurrentCompany.state_id.name,
            'country_id': getCurrentCompany.country_id.name
        }

        if getCurrentCompany.street:
            street = str(values['street'])
        if getCurrentCompany.street2:
            street2 = str(values['street2'])
        if getCurrentCompany.city:
            city = str(values['city'])
        if getCurrentCompany.zip:
            zip = values['zip']
        if getCurrentCompany.state_id.name:
            state = str(values['state_id'])
        if getCurrentCompany.country_id.name:
            country = str(values['country_id'])

        return street +' '+ street2 +' '+ city + ' '+ zip + ' '+ state + ' '+ country

    def get_product_categs_path(self, id):
        """
        To render full path for breadcrumbs based on argument
        :param id: product.public.category
        :return: list of category path and website url
        """
        categ_set = []
        if id:
            while id:
                categ = self.env['product.public.category'].sudo().search([('id', '=', id)])
                categ_set.append(categ.id)
                if categ and categ.parent_id:
                    id = categ.parent_id.id
                else:
                    break

        # For Reverse order
        categ_set = categ_set[::-1]

        values = {
            'categ_set': categ_set,
            'web_url': self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        }
        return values

    def get_min_max_prices(self, search=False, category=False, attributes=False):
        """
        Get minimum price and maximum price according to Price list as well as discount for Shop page
        :return: min and max price value
        """
        range_list = []
        cust_min_val = request.httprequest.values.get('min_price', False)
        cust_max_val = request.httprequest.values.get('max_price', False)

        domain = WebsiteSaleWishlist._get_search_domain(self, search=search, category=category,
                                                        attrib_values=attributes)

        if attributes:
            ids = []
            for value in attributes:
                if value[0] == 0:
                    ids.append(value[1])
                    domain += [('product_brand_ept_id.id', 'in', ids)]
        products = self.env['product.template'].search(domain)
        prices_list = []
        if products:
            pricelist = self.get_current_pricelist()
            for prod in products:
                context = dict(self.env.context, quantity=1, pricelist=pricelist.id if pricelist else False)
                product_template = prod.with_context(context)

                list_price = product_template.price_compute('list_price')[product_template.id]
                price = product_template.price if pricelist else list_price
                if price:
                    prices_list.append(price)

        if not prices_list: return False

        range_list.append(round(min(prices_list), 2))
        range_list.append(round(max(prices_list), 2))
        return range_list

    def get_brand(self, products=False):
        """
        This function is used to search the list of brand data
        :return: List of brand
        """

        if products:
            shop_brands = self.env['product.brand.ept'].sudo().search([('product_ids', 'in', products.ids), ('products_count', '>', 0),('website_id', 'in', (False, self.get_current_website().id))])
        else:
            shop_brands = self.env['product.brand.ept'].sudo().search(
                [('website_published', '=', True), ('products_count', '>', 0),
                 ('website_id', 'in', (False, self.get_current_website().id))])
        return shop_brands

    def image_resize(self, img, width, height):
        """
        This function is used for resize the image with specific height and width
        and return the resizable image.
        :param img: image url
        :param width: image width
        :param height: image height
        :return: resizable image url
        """
        return image_process(img, size=(width, height))

    def get_carousel_category_list(self):
        """
        This method is used for return the list of category
        which has selected the allow category in carousel option from admin
        :return: list of category.
        """
        domain = [('website_id', 'in', (False, self.get_current_website().id)),
                  ('allow_in_category_carousel', '=', True)]
        category = self.env['product.public.category'].sudo().search(domain)
        return category

    def checkQuickFilter(self, currentWebsite, filterWebsiteArray):
        if currentWebsite in filterWebsiteArray or len(filterWebsiteArray) == 0:
            return True
        else:
            return False

    def list_providers_ept(self):
        """
        This method is used for return the encoded url for the auth providers
        :return: link for the auth providers.
        """
        try:
            providers = request.env['auth.oauth.provider'].sudo().search_read([('enabled', '=', True)])
        except Exception:
            providers = []
        for provider in providers:
            return_url = request.httprequest.url_root + 'auth_oauth/signin'
            state = OAuthLogin.get_state(self, provider)
            params = dict(
                response_type='token',
                client_id=provider['client_id'],
                redirect_uri=return_url,
                scope=provider['scope'],
                state=json.dumps(state),
            )
        return werkzeug.url_encode(params)
