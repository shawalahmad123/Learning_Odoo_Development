odoo.define('emipro_theme_base.quick_view', function(require) {
    'use strict';

    var sAnimations = require('website.content.snippets.animation');
    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    var WebsiteSale = new sAnimations.registry.WebsiteSale();
    var theme_script = new sAnimations.registry.product_detail();

    publicWidget.registry.quickView = publicWidget.Widget.extend({
        selector: "#wrapwrap",
        events: {
            'click .quick-view-a': 'initQuickView',
        },
        initQuickView: function(ev) {
            /* This method is called while click on the quick view icon
             and show the model and quick view data */
            ev.preventDefault()
            self = this;
            var element = ev.currentTarget;
            var product_id = $(element).attr('data-id');
            ajax.jsonRpc('/quick_view_item_data', 'call',{'product_id':product_id}).then(function(data) {
                if($("#wrap").hasClass('js_sale'))
                {
                    $("#quick_view_model_shop .modal-body").html(data);
                    $("#quick_view_model_shop").modal({keyboard: true});
                }else {
                    $("#quick_view_model .modal-body").html(data);
                    $("#quick_view_model").modal({keyboard: true});
                }
                var WebsiteSale = new sAnimations.registry.WebsiteSale();
                WebsiteSale.init();

                setTimeout(function(){
                    theme_script.productGallery();
                    $('#mainSlider .owl-carousel').trigger('refresh.owl.carousel');
                    $('#thumbnailSlider .owl-carousel').trigger('refresh.owl.carousel');
                }, 200);
                $('.variant_attribute  .list-inline-item').first().addClass('active_li');
                $(".variant_attribute li").each(function() {
                    if($(this).find('.css_attribute_color').hasClass('active')) {
                        $(this).parent('.list-inline-item').addClass('active_li');
                    }
                });

                $( ".list-inline-item .css_attribute_color" ).change(function() {
                    $('.list-inline-item').removeClass('active_li');
                    $(this).parent('.list-inline-item').addClass('active_li');
                });

            });

        },
    });
});