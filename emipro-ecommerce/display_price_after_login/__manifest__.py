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
  "name"                 :  "Website Show Price After Login",
  "summary"              :  """Mark website products as Exclusive for members only""",
  "category"             :  "eCommerce",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/odoo-website-show-price-after-login.html",
  "description"          :  """The module facilitates you to hide the prices of selected website products. Only logged in users or members will be able to see the prices of such products. Moreover, do you have products or services whose prices depend upon customers' requirements? Then, the module allows you to unpublish the price of the products and add a contact mail address to the product page. The customer needs to contact the admin to get the price of these products/services.""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=display_price_after_login&custom_url=/shop",
  "depends"              :  [
                             'website_sale',
                             'website_webkul_addons',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/product.xml',
                             'views/res_config_views.xml',
                             'wizard/price_visibility_update.xml',
                             'templates/web.xml',
                             'data/data.xml',
                            ],
  "demo"                 :  ['demo/demo.xml'],
  "images"               :  ['static/description/banner.png'],
  "application"          :  True,
  "price"                :  15.0,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}