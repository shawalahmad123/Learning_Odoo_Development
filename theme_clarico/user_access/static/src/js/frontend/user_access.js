odoo.define('user_access.user_access_js', function(require) {
    'use strict';

    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var session = require('web.session');

     publicWidget.registry.te_brand_slider = publicWidget.Widget.extend({
        selector: "#wrapwrap",
        start: function () {
            self = this;
            self.hideAddToCart();
        },
        hideAddToCart: function() {
            var user = session.user_id
            if (user == false)
            {
                $(document).find(".fa-shopping-cart").parent().remove();
            }
        }
    });
});