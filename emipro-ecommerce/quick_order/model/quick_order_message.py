# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################

from odoo import models, fields, api
import logging
_log = logging.getLogger(__name__)

class ResConfigSetting(models.TransientModel):
    _inherit = "res.config.settings"

    def get_quick_form(self):
        template = self.env.ref("quick_order.quick_order_message_from_view").id
        res_id = self.env['quick.order.message'].search([], limit = 1)
        return {
            "name" : "Quick Order Message",
            "type" : "ir.actions.act_window",
            "res_model" : "quick.order.message",
            "view_mode" : "form",
            "view_type" : "form",
            "res_id" : res_id.id,
            "view_id" : template
        }

class QuickOrderMessage(models.Model):
    _name = 'quick.order.message'

    name = fields.Char(string = "Quick Order Message", default = 'Quick Order Message')
    message_on_empty_order_list = fields.Char(string = "Message on empty Order list", default = lambda self : self.get_message_1(), required = True, translate = True)
    message_on_product_search = fields.Char(string = "Message on no Product found in search", default = lambda self: self.get_message_3(), required = True, translate = True)
    message_on_empty_shopping_list = fields.Char(string = "Message on empty Shopping list", default = lambda self: self.get_message_4(), required = True, translate = True)
    message_on_delete_all_products = fields.Char(string = "Message on delete all products from Quick Order list", default = lambda self: self.get_message_5(), required = True, translate = True)
    empty_shopping_list_submit = fields.Char(string = "Message on submit empty Shopping list into Cart", default = lambda self: self.get_message_6(), required = True, translate = True)

    def get_message_1(self):
        return "No Products found in your Order list"

    def get_message_3(self):
        return "No Products found for the related keyword"

    def get_message_4(self):
        return "No Shopping List available. Please create a new one"

    def get_message_5(self):
        return "All Products are successfully deleted from your Quick Order list"

    def get_message_6(self):
        return "No Products in your Shopping list for added into the Order Cart"
