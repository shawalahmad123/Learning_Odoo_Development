# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Website Quick Order",
  "summary"              :  """Easy to create Quick Order list and Shopping lists, Manage these lists quickly for placing order into the Cart""",
  "category"             :  "website",
  "version"              :  "1.3.5",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Quick-Order.html",
  "description"          :  """Add the Products in a list and create a Quick Order/ Bulk Order for these product.
                    Add the Products in the shopping lists and save time, by simply adding them in cart in bulk.""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=quick_order&custom_url=/quickorder",
  "depends"              :  [
                             'website_sale',
                             'sale',
                             'website_sale_stock',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/add_assets.xml',
                             'views/quick_order_template.xml',
                             'views/quick_order_message.xml',
                             'views/res_config_setting_view.xml',
                             'views/quick_order_view.xml',
                            ],
  "demo"                 :  ['data/quick_order_demo_data.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  169,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}
