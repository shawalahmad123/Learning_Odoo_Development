/**************************************************
        01. Search in Header
        02. Page Scroll up
        03. Theme Wishlist
        04. Shop Events
        05. cart Popover
        06. Theme layout
        07. Compare short name
**************************************************/
odoo.define('theme_clarico_vega.theme_script', function(require) {
    'use strict';

    var sAnimations = require('website.content.snippets.animation');
    var publicWidget = require('web.public.widget');
    var Widget = require('web.Widget');
    var core = require('web.core');
    var _t = core._t
    var ajax = require('web.ajax');
    var config = require('web.config');
    var sale = new sAnimations.registry.WebsiteSale();

    //------------------------------------------
    // 01. Search in Header
    //------------------------------------------
    sAnimations.registry.themeSearch = sAnimations.Class.extend({
        selector: '#wrapwrap',
        read_events: {
            'click .te_srch_icon': '_onSearchClickOpen',
            'click .te_srch_close': '_onSearchClickClose',
            'click .mycart-popover .js_delete_product': '_onClickDeleteProduct',
        },
        start: function() {
            if ($(window).innerWidth() > 1200) {
                $("#top_menu > .dropdown").each(function() {
                    if (!$(this).closest(".o_extra_menu_items").length) {
                        $(this).closest("a").click(function() {
                            return false;
                        });
                        $(this).hover(function() {
                            $(this).toggleClass('open');
                            $(this).find(".dropdown-menu").toggleClass('te_mega_animation');
                            $(this).removeClass('show');
                            $(this).find('.dropdown-menu').removeClass('show');
                        }, function() {
                            $(this).toggleClass('open');
                            $(this).find(".dropdown-menu").toggleClass('te_mega_animation');
                            $(this).removeClass('show');
                            $(this).find('.dropdown-menu').removeClass('show');
                        });
                    }
                });
            }

            $('.variant_attribute  .list-inline-item').first().addClass('active_li');
            $( ".list-inline-item .css_attribute_color" ).change(function() {
                $('.list-inline-item').removeClass('active_li');
                $(this).parent('.list-inline-item').addClass('active_li');
            });

             /*Ipad/Mobile Hamburger Menu*/
            $('.te_header_9_navbar').find('.navbar-toggler').append('<input type="checkbox" id="check" class="menu_checkbox"><label for="check" class="label_checkbox"><div class="btn_menu" id="btn_menu"><span></span><span></span><span></span></div></label>');

        },
        _onSearchClickOpen: function(ev) {
            var self = ev.currentTarget;
            //style1
            if ($(".te_header_1_right").length) {
                $(".te_search_popover").addClass("visible");
                $(self).css("display", "none");
                $(".te_srch_close").css("display", "block");
                setTimeout(function(){
                    $('input[name="search"]').focus();
                }, 500);
            }
            //style 2 3 and 4 resp view
            if ($(window).width() < 768) {
                if ($(".te_header_style_2_right").length || $(".te_header_3_search").length || $(".te_header_style_4_inner_first").length) {
                    $(".te_search_popover").addClass("visible");
                    $(self).css("display", "none");
                    $(".te_srch_close").css("display", "block");
                    setTimeout(function(){
                        $('input[name="search"]').focus();
                    }, 500);
                }
            }
            //style5
            if ($(".te_header_5_search").length) {
                $(".te_search_5_form").addClass("open_search");
                var $h_menu = $("#oe_main_menu_navbar").height();
                $(".te_search_5_form").css({
                    top: $h_menu + 0
                });
                setTimeout(function(){
                    $('input[name="search"]').focus();
                }, 500);
            }
            //style6
            if ($(".te_header_6_srch_icon").length) {
                $(".te_header_before_right").addClass("search_animate");
                if ($(window).width() < 768) {
                    $(".te_header_before_left").addClass("search_animate");
                }
                $(".te_header_search input").css("width","100%");
                setTimeout(function(){
                    if ($(window).width() > 768) {
                        $(".te_header_before_right").css("display","none");
                    }else{
                        $(".te_header_before_right").css("display","none");
                        $(".te_header_before_left").css("display","none");
                    }
                    $(".te_header_search").css("display","block");
                    $('input[name="search"]').focus();
                }, 500);
            }
            //style7
            if ($(".te_searchform__popup").length) {
                $(".te_searchform__popup").addClass("open");
                $(".te_srch_close").css("display", "block");
                setTimeout(function(){
                    $('input[name="search"]').focus();
                }, 500);
            }
            //style9 and style11
            if ($(".te_header_9_srch_icon, .te_header_11_srch_icon").length) {
                $(".te_header_right_icon").addClass("search_animate");
                if($(window).width() <= 767){
                    if($('.te_header_11_srch_icon').length){
                        $('.navbar-expand-md .navbar-toggler').hide();
                        $('.te_header_11_srch_icon').hide();
                        $('header .navbar-brand.logo').hide();
                    }
                    else{
                        $(".navbar-expand-md .navbar-toggler").hide();
                    }
                }
                if ($(window).width() <= 991) {
                    if($('.te_header_11_srch_icon').length){
                        $('.te_header_11_srch_icon').hide();
                        $("div#top_menu_collapse .navbar-nav, div#top_menu_collapse_clone .navbar-nav").hide();
                    }
                    else{
                        $(".navbar-expand-md .navbar-nav").hide();
                        $(".navbar-expand-md .navbar-nav").addClass("search_animate");
                        $(".te_header_right_icon").hide();
                        $('.te_header_navbar label.label_checkbox').hide();
                        $("div#top_menu_collapse .navbar-nav").hide();
                    }
                }
                $(".te_header_search input").css("width","100%");
                setTimeout(function(){
                    if ($(window).width() >= 992) {
                        $(".te_header_right_icon").css("display","none");
                        $(".navbar-expand-md .navbar-nav").hide();
                    }
                    $(".te_header_search_popover").fadeIn(200);
                }, 500);
            }
            //style10
            if ($(".te_srch_icon_mobile_header").length) {
                setTimeout(function(){
                    $('input[name="search"]').focus();
                }, 500);
                if ($(window).width() <= 991) {
                    $(".te_header_10_search").addClass("active");
                    $(".navbar-expand-md .navbar-nav").hide();
                    $(self).hide()
                    $(".te_srch_close").show();
                }
            }
        },
        _onSearchClickClose: function(ev) {
            var self = ev.currentTarget;
            //style1
            if ($(".te_header_1_right").length) {
                $(".te_search_popover").removeClass("visible");
                $(self).css("display", "none");
                $(".te_srch_icon").css("display", "block");
            }
            //style 2 and 3 resp view
            if ($(window).width() < 768) {
                if ($(".te_header_style_2_right").length || $(".te_header_3_search").length || $(".te_header_style_4_inner_first").length) {
                    $(".te_search_popover").removeClass("visible");
                    $(self).css("display", "none");
                    $(".te_srch_icon").css("display", "block");
                }
            }
            //style5
            if ($(".te_header_5_search").length) {
                $(".te_search_5_form").removeClass("open_search");
                $(".te_search_icon_5").css("display", "inline-block");
            }
            //style6
            if ($(".te_header_6_srch_icon").length) {
                $(".te_header_before_right").removeClass("search_animate").css("display", "block");
                $(".te_header_before_left").removeClass("search_animate").css("display","block"); /*changes for show left header block*/
                $(".te_header_search").css("display", "none");
                $(".te_header_search input").css("width", "0%");
                $(".te_srch_icon").css("display", "inline-block")
            }
            //style7
            if ($(".te_searchform__popup").length) {
                $(".te_searchform__popup").removeClass("open");
                $(".te_srch_icon").css("display", "block");
            }
            //style9 and style11
            if ($(".te_header_9_srch_icon, .te_header_11_srch_icon").length) {
                $(".te_header_right_icon").removeClass("search_animate").css("display", "block");
                $(".navbar-expand-md .navbar-nav").removeClass("search_animate").show();
                $(".te_header_search_popover").css("display", "none");
                $(".te_header_search_popover input").css("width", "0%");
                $(".te_srch_icon").css("display", "inline-block");
                if($(window).width() <= 767){
                    if($('.te_header_11_srch_icon').length){
                        $('.navbar-expand-md .navbar-toggler').fadeIn(300);
                        $('.te_header_11_srch_icon').fadeIn(300);
                        $('header .navbar-brand.logo').fadeIn(300);
                    }
                    else{
                        $(".navbar-expand-md .navbar-toggler").fadeIn(300);
                    }
                }
                if ($(window).width() <= 991) {
                    if($('.te_header_11_srch_icon').length){
                        $("div#top_menu_collapse .navbar-nav, div#top_menu_collapse_clone .navbar-nav").fadeIn(400);
                    }
                    else{
                        $(".te_header_right_icon").fadeIn(300);
                        $(".navbar-expand-md .navbar-nav").fadeIn(400);
                        $('.te_header_navbar label.label_checkbox').fadeIn(400);
                    }
                }
            }
            //style10
            if ($(".te_srch_icon_mobile_header").length) {
                if ($(window).width() <= 991) {
                    $(".te_header_10_search").removeClass("active");
                    $(".navbar-expand-md .navbar-nav").show();
                    $(".te_srch_close").hide();
                    $(".te_srch_icon").show();
                }
            }
        },
    });

    //------------------------------------------
    // 02. Page Scroll up
    //------------------------------------------
    sAnimations.registry.themeLayout = sAnimations.Class.extend({
        selector: '.o_footer',
        read_events: {
            'click .scrollup-div': '_onClickAnimate',
        },
        _onClickAnimate: function(ev) {
            $("html, body").animate({
                scrollTop: 0
            }, 1000);
        },
    });
    //------------------------------------------
    // 03. Theme Wishlist
    //------------------------------------------
    sAnimations.registry.themeWishlist = sAnimations.Class.extend({
        selector: '#o_comparelist_table',
        read_events: {
            'click .o_wish_rm': '_onRemoveClick',
        },
        _onRemoveClick: function(ev) {
            var ajax = require('web.ajax');
            var tr = $(ev.currentTarget).parents('tr');
            var wish = tr.data('wish-id');
            var route = '/shop/wishlist/remove/' + wish;
            ajax.jsonRpc(route, 'call', {
                'wish': wish
            }).then(function(data) {
                $(tr).hide();
                if ($('.t_wish_table tr:visible').length == 0) {
                    window.location.href = '/shop';
                }
            })
        },

    });

    //------------------------------------------
    // 04. Shop Events
    //------------------------------------------
    sAnimations.registry.themeEvent = sAnimations.Class.extend({
        selector: '.oe_website_sale',
        read_events: {
            'click .te_attr_title': '_onAttribSection',
            'click .te_view_more_attr': '_onViewMore',
            'click .te_view_less_attr': '_onViewLess',
            'click .te_shop_filter_resp': '_onRespFilter',
            'click .te_filter_close': '_onFilterClose',
            'click .te_color-name':'_oncolorattr',
            'click .te_show_category':'_onShowCategBtnResp',
            'click .te_show_option':'_onShowOptionBtnResp',
            'click .te_ctg_h4': '_onCategorySection',
        },
        start: function() {
            $("img.lazyload").lazyload();
            this.onShowClearVariant();
            this.onSelectAttribute();
        },
        onShowClearVariant: function() {
            $("form.js_attributes .te_shop_attr_ul input:checked, form.js_attributes .te_shop_attr_ul select").each(function() {
                var self = $(this);
                var type = ($(self).prop("tagName"));
                var type_value;
                var attr_value;
                var attr_value_str;
                var attr_name;
                var target_select;
                var curr_parent;
                var target_select = self.parents("li.nav-item").find("a.te_clear_all_variant");
                if ($(type).is("input")) {
                    type_value = this.value;
                    attr_value = $(this).parent("label").find("span").html();
                    if (attr_value) {
                        attr_value_str = attr_value.toLowerCase();
                        attr_value_str = attr_value_str.replace(/(^\s+|[^a-zA-Z0-9 ]+|\s+$)/g,"");
                        attr_value_str = attr_value_str.replace(/\s+/g, "-");
                    }
                    curr_parent = self.parents("ul");
                    target_select = curr_parent.parent("li.nav-item").find("a.te_clear_all_variant");
                    attr_name = curr_parent.parent("li.nav-item").find("a.te_clear_all_variant").attr('attribute-name');
                    if (self.parent("label").hasClass("css_attribute_color")) {
                        attr_value = self.parent("label").siblings(".te_color-name").html();
                        if(attr_value) {
                            attr_value_str = attr_value.toLowerCase();
                            attr_value_str = attr_value_str.replace(/(^\s+|[^a-zA-Z0-9 ]+|\s+$)/g,"");
                            attr_value_str = attr_value_str.replace(/\s+/g, "-");
                        }
                    }
                    var first_li = self.closest("ul").find("li").first();
                    var selected_li = self.closest("li.nav-item");
                    $(first_li).before(selected_li);
                    if (!curr_parent.hasClass("open_ul")) {
                        curr_parent.parent("li.nav-item").find('.te_attr_title').click();
                    }
                } else if ($(type).is("select")) {
                    type_value = self.find("option:selected").val();
                    attr_value = self.find("option:selected").html();
                    if(attr_value) {
                        attr_value_str = attr_value.toLowerCase();
                        attr_value_str = attr_value_str.replace(/(^\s+|[^a-zA-Z0-9 ]+|\s+$)/g,"");
                        attr_value_str = attr_value_str.replace(/\s+/g, "-");
                    }
                    attr_name = self.find("option:selected").parents("li.nav-item").find('a.te_clear_all_variant').attr('attribute-name');
                    target_select = self.parents("li.nav-item").find("a.te_clear_all_variant");
                }
                if (type_value) {
                    $(".te_clear_all_form_selection").css("display", "inline-block");
                    $(".te_view_all_filter_div").css("display", "inline-block");
                    if (target_select) {
                        $(".te_view_all_filter_inner").append("<div class='attribute'>" + attr_value + "<a data-id='" + type_value + "' class='te_clear_attr_a "+attr_name+" "+attr_value_str+" '>x</a></div>");
                    }
                }
            });
            $("form.js_attributes input:checked, form.js_attributes select").each(function() {
                var self = $(this);
                var type = ($(self).prop("tagName"));
                var target_select = self.parents("li.nav-item").find("a.te_clear_all_variant");
                var type_value;
                if ($(type).is("input")) {
                    type_value = this.value;
                    var first_li = self.closest("ul").find("li").first();
                    var selected_li = self.closest("li.nav-item");
                    $(first_li).before(selected_li);
                } else if ($(type).is("select")) {
                    type_value = self.find("option:selected").val();
                }
                if (type_value) {
                    target_select.css("display", "inline-block");
                }
            });
        },

        // If any attribute are selected then automatically this section is Expand(only for type select)
        onSelectAttribute: function(ev){
            $("form.js_attributes .te_shop_attr_ul input:checked, form.js_attributes .te_shop_attr_ul select").each(function() {
                var self = $(this);
                var type = ($(self).prop("tagName"));
                var type_value;
                if ($(type).is("select")) {
                    type_value = self.find("option:selected").val();
                }
                if (type_value) {
                    self.addClass("open_select").css('display','inline-block');
                    self.siblings('.te_attr_title').addClass('te_fa-minus');
                }
            });
        },
        _onClearAttribInd: function(ev) {
            var self = ev.currentTarget;
            var id = $(self).attr("data-id");
            if (id) {
                $("form.js_attributes option:selected[value=" + id + "]").remove();
                $("form.js_attributes").find("input[value=" + id + "]").removeAttr("checked");
            }
            ajaxorformload(ev);
        },
        _onClearAttribAll: function(ev) {
            $("form.js_attributes option:selected").remove();
            $("form.js_attributes").find("input:checked").removeAttr("checked");
            ajaxorformload(ev);
        },
        _onClearAttribDiv: function(ev) {
            var self = ev.currentTarget;
            var curent_div = $(self).parents("li.nav-item");
            var curr_divinput = $(curent_div).find("input:checked");
            var curr_divselect = $(curent_div).find("option:selected");
            _.each(curr_divselect, function(ev) {
                $(curr_divselect).remove();
            });
            _.each(curr_divinput, function(ev) {
                $(curr_divinput).removeAttr("checked");
            });
            ajaxorformload(ev);
        },
        _onCategorySection: function(){
            var ctg_ul = $('.te_ctg_h4').siblings('.te_shop_ctg_list');
             if (ctg_ul.hasClass("open_ul")) {
                ctg_ul.removeClass("open_ul");
                ctg_ul.siblings(".te_ctg_h4").addClass('te_fa-plus');
                ctg_ul.toggle('slow');
            }
            else{
                ctg_ul.addClass("open_ul");
                ctg_ul.siblings(".te_ctg_h4").removeClass('te_fa-plus');
                ctg_ul.toggle('slow');
            }
        },
        _onAttribSection: function(ev) {
            var self = ev.currentTarget;
            var main_li = $(self).parents("li.nav-item");
            var ul_H = main_li.find("ul").height();
            if (main_li.find("select").length == 1) {
                $("select.form-control.open_select").css('display','block');
                var main_select = main_li.find("select");
                if (main_select.hasClass("open_select")) {
                    main_select.removeClass("open_select");
                    main_select.parent(".nav-item").find(".te_attr_title").removeClass('te_fa-minus');
                    main_select.toggle('slow');
                }
                else {
                    main_select.addClass("open_select");
                    main_select.parent(".nav-item").find(".te_attr_title").addClass('te_fa-minus');
                    main_select.toggle('slow');
                }
            }
            var main_ul = main_li.find("ul");

            if (main_ul.hasClass("open_ul")) {
                main_ul.removeClass("open_ul");
                $(main_ul).parent('.nav-item').find(".te_attr_title").removeClass('te_fa-minus');
                main_ul.toggle('slow');

                main_li.find('.te_view_more_attr').removeClass('active');
                main_li.find('.te_view_more_attr').css("display", "none");
            } else {
                main_ul.addClass("open_ul");
                $(main_ul).parent('.nav-item').find(".te_attr_title").addClass('te_fa-minus');
                main_ul.toggle('slow');

                if (ul_H >= 190) {
                    main_li.find('.te_view_more_attr').addClass('active');
                    main_li.find('.te_view_more_attr').css("display", "inline-block");
                }
            }
        },
        _onViewMore: function(ev) {
            var self = ev.currentTarget;
            var clicks = $(self).data('clicks');
            $(self).parent('li.nav-item').find('ul').css({
                "overflow": "auto"
            });
            $(self).addClass('d-none').removeClass('active').hide();
            $(self).siblings('.te_view_less_attr').removeClass('d-none').addClass('active').css('display','inline-block');
            $(self).data("clicks", !clicks);
        },
        /* Added for show less attribute */
        _onViewLess: function(ev) {
            var self = ev.currentTarget;
            var clicks = $(self).data('clicks');
            $(self).parent('li.nav-item').find("ul").css({
                "overflow": "hidden"
            });
            $(self).addClass('d-none').removeClass('active').hide();
            $(self).siblings('.te_view_more_attr').removeClass('d-none').addClass('active').css('display','inline-block');
            $(self).data("clicks", !clicks);
            $(self).parent('li.nav-item').find('.nav-pills').animate({
                scrollTop: 0
            }, 'slow');
        },
        _onRespFilter: function(ev) {
            $("#products_grid_before").toggleClass("te_filter_slide");
            $("#wrapwrap").toggleClass("wrapwrap_trans");
            $('body').css("overflow-x", "hidden");
            $("#wsale_products_attributes_collapse").addClass("show");
            if($('#products_grid_before').find('#wsale_products_attributes_collapse').length < 1) {
                $("#wsale_products_categories_collapse").addClass("show");
                if($("#wsale_products_categories_collapse .show")){
                    $(".te_show_category").find("i").addClass('fa-chevron-down').removeClass('fa-chevron-right');
                }
            }
            if($("#wsale_products_attributes_collapse .show")){
                $(".te_show_option").find("i").addClass('fa-chevron-down').removeClass('fa-chevron-right');
            }
        },
        _onFilterClose: function(ev) {
            $("#products_grid_before").removeClass("te_filter_slide")
            $("#wrapwrap").removeClass("wrapwrap_trans");
        },
        _oncolorattr: function(ev){
            var self=ev.currentTarget;
             //$(self).parents("li.color-with-name-divmaxW").find("input").click();
             $(self).parent().find("input").click();
        },
         _onShowCategBtnResp: function(ev){
            $(".te_show_category").find("i").toggleClass('fa-chevron-right fa-chevron-down');
        },
        _onShowOptionBtnResp: function(ev){
            $(".te_show_option").find("i").toggleClass('fa-chevron-down fa-chevron-right');
        },
    });
    /*---- Shop Functions ------*/
    //function for ajax form load
    function ajaxorformload(ev) {
        var ajax_load = $(".ajax_loading").val();
        if (ajax_load == 'True') {
            ajaxform(ev);
        } else {
            $("form.js_attributes input,form.js_attributes select").closest("form").submit();
        }
    }
    sAnimations.registry.WebsiteSale.include({
        /*
         Adds the stock checking to the regular _onChangeCombination method
        @override
        */
        _updateProductImage: function (){

        this._super.apply(this, arguments);
        },
    });




    /** Product image gallery for product page */
    sAnimations.registry.product_detail = sAnimations.Class.extend({
        selector: "#product_detail",
        start: function() {
            this.productStickyGallery();
        },
        productGallery: function(){
            var slider = $('#mainSlider .owl-carousel');
            var thumbnailSlider = $('#thumbnailSlider .owl-carousel');
            $('#thumbnailSlider').show();
            var duration = 400;
            var img_length = $('#len-ept-image').val();

            if($('#len-ept-image').val() < 2) {
                $('#mainSlider').addClass('mainslider-full');
            }

            if($('#len-ept-image').val() > 5) {
                var slider_length = ($('#len-ept-image').val() - 2);
                var thumb_length =  $('#len-ept-image').val() - ($('#len-ept-image').val() - 5);
            } else {
                var slider_length = 0;
                var thumb_length = 0;
            }
            slider.owlCarousel({
                nav:true,
                navText : ['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
                items:1,
                lazyLoad:true,
                loop: $('#len-ept-image').val() > 1 ? true : false,
                rewind: true,
            }).on('changed.owl.carousel', function (event) {
                // On change of main item to trigger thumbnail item
                let currentIndex = event.item.index + slider_length;
                thumbnailSlider.trigger('to.owl.carousel', [currentIndex, duration, true]);
                if($('#len-ept-image').val() <= 5) {
                    thumbnailSlider.find('.owl-item').removeClass('center');
                    thumbnailSlider.find('.owl-item').eq(currentIndex - 2).addClass('center');
                }
            });

                // carousel function for thumbnail slider
            thumbnailSlider.owlCarousel({
                loop: $('#len-ept-image').val() > 5 ? true : false,
                center: $('#len-ept-image').val() > 5 ? true : false,
                margin: 4,
                nav:true,
                navText : ['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
                responsive:{
                    0:{
                        items:5,
                    },
                    600:{
                        items:5
                    },
                    1000:{
                        items:5
                    }
                }
            }).on('click', '.owl-item', function () {
                // On click of thumbnail items to trigger same main item
                let currentIndex = $(this).find('li').attr('data-slide-to');
                slider.trigger('to.owl.carousel', [currentIndex, duration, true]);
            }).on('refreshed.owl.carousel', function () {
                if($('#len-ept-image').val() <= 5) {
                    $('#thumbnailSlider .owl-carousel .owl-item').first().addClass('center');
                }
            });

            var thumb_width = $('#thumbnailSlider').find('.owl-item').width();
            $('#thumbnailSlider').find('.owl-item').height(thumb_width);
            if ($(window).width() > 767) {
                if($('.o_rtl').length == 1){
                    $('#thumbnailSlider').find('.owl-carousel').css('right', (0-(thumb_width*2)));
                }
                $('#thumbnailSlider').find('.owl-carousel').css('left', (0-(thumb_width*2)));
                $('#thumbnailSlider').find('.owl-carousel').css('top', (thumb_width*2)+26);
            }
        },
        productStickyGallery: function(){
            if($( window ).width() > 991) {
                var $sticky = $('#product_detail .row > .col-lg-6:first-child');
                if (!!$sticky.offset()) {
                    var sidebar_height = $sticky.innerHeight();
                    var stickyTop = $sticky.offset().top;
                    $(window).scroll(function(){
                        if($('#oe_main_menu_navbar').length) {
                            var header_height = $('#oe_main_menu_navbar').height() + $('.te_header_navbar').height() + 20;
                        } else {
                            var header_height = $('.te_header_navbar').height() + 20;
                        }
                        var stickOffset = header_height;
                        var windowTop = $(window).scrollTop();
                        if (stickyTop < windowTop+stickOffset+stickOffset) {
                            $sticky.css({ position: 'sticky', top: stickOffset });
                            $sticky.addClass('sticky-media');
                        } else {
                            $sticky.css({ position: 'relative', top: 'initial'});
                            $sticky.removeClass('sticky-media');
                        }
                    });
                }
            }
        },
    });


    //------------------------------------------
    // 06. Theme layout
    //------------------------------------------

    $(document).ready(function($) {
        if($(document).find('.te_recently_viewed'))
        {
            var r_name = $("#te_rect_cnt").text();
            $('.te_recently_viewed').find('h6').each(function(){

                $(document).find('h6.card-title').addClass("te_rect_name")
                if(r_name == 2)
                {
                    $('h6.card-title').addClass('te_2_line');
                }
                if(r_name == 3)
                {
                    $('h6.card-title').addClass('te_3_line');
                }
            });
        }
        if($('.o_comparelist_button')) {
            setTimeout(function(){
                $('.o_comparelist_button').find('a').addClass('te_theme_button');
            }, 700);
        }
        setTimeout(function(){
            $(".o_portal_chatter_composer_form").find("button").addClass("te_theme_button");
            $(".js_subscribe_btn").addClass("te_theme_button");
            $(".o_portal_sign_submit").addClass("te_theme_button");
        }, 1000);

        //extra menu dropdown
        $('.o_extra_menu_items .dropdown-menu').css("display", "none")
        $('li.o_extra_menu_items .dropdown').click(function(event) {
            event.stopImmediatePropagation();
            $(this).find(".dropdown-menu").slideToggle();
        });
        //Header top when transparent header
        var header_before_height = $(".te_header_before_overlay").outerHeight();
        if ($("body").find(".o_header_overlay").length > 0) {
            $("header:not(.o_header_affix)").addClass("transparent_top")
            $(".transparent_top").css("top", header_before_height);
            $(".o_header_affix.affix").removeClass("transparent_top")
        }
        //Category mega menu
        var li_pos = $('.te_dynamic_ept').index()
        if(li_pos<3) {
            $('#custom_menu').css("left","-20%");
        }
        else if(li_pos>=3 && li_pos<6)
        {
            $('#custom_menu').css({"left":"auto", "right": "-70%"});
        }
        else {
            $('#custom_menu').css({"left":"auto", "right": "-20%"});
        }
        if($(document).find('#wrapwrap').hasClass('o_rtl'))
        {
            $('#custom_menu').css({"left":"-20%", "right": "auto"});
        }
        $("#custom_menu li").each(function() {
            var has_ctg = $(this).find("ul.t_custom_subctg").length > 0
            if (has_ctg) {
                $(this).append("<span class='ctg_arrow fa fa-angle-right' />")
                 var ul_index = 0;
                $(document).on('click',".ctg_arrow",function(ev) {
                    var $this = $(this),
                    $lst = $('<div class="te_list_ctg_name"></div>');
                    $this.parents('li#custom_menu_li').each(function(n, li) {
                          var $a = $(li).children('a').clone();
                          $a.attr("href", "#");
                          $lst.prepend(' <span class="te_main_a">/ </span> ', $a);
                    });
                    $('.te_breadcrumb_ctg').html( $lst.prepend('<a href="/shop">Shop</a>') );

                    var self = $(this).siblings("ul.t_custom_subctg");
                    ul_index = $(self).parents("ul").length == 0 ? $(self).parents("ul").length : ul_index + 1;
                    $(self).stop().animate({
                        width: "100%"
                    });
                    $('.te_main_a').parent().removeClass("te_active");
                    $(this).siblings('.te_main_a').parent().addClass("te_active");
                    $(this).siblings('#custom_recursive').find('.t_custom_subctg').css({
                        "display": "none",
                        "transition": "0.3s easeout",
                        "left": "unset",
                        "z-index": 'auto'
                    });
                    $(self).css({
                        "display": "block",
                        "transition": "0.3s easeout",
                        "left": "auto",
                        "right": "0",
                        "z-index": ul_index
                    });
                    if($(document).find('#wrapwrap').hasClass('o_rtl')){
                        $(self).css({
                            "right": "auto",
                            "left": "0",
                        });
                        $(this).parents('#te_main_ul').children('li').children('ul').css({
                            "left":"0",
                            "right": "100%",
                        });
                    }
                    $(this).parents('#te_main_ul').children('li').children('ul').css("left", "100%");
                    $(self).parent().parent(".t_custom_subctg").css("overflow-y", "hidden");
                    $(self).parent().parent(".t_custom_subctg").scrollTop(0);
                    $(this).parents("#custom_menu").scrollTop(0);
                    $(this).parents("#custom_menu").css("overflow-y", "hidden");
                })
                $(document).on('click',".te_prent_ctg_heading",function(ev) {
                    $(this).parent("ul#custom_recursive").stop().animate({
                        width: "0"
                    }, function() {

                        var $this = $(this),
                        $lst = $('<div class="te_list_ctg_name"></div>');
                        $this.parents('li#custom_menu_li').each(function(n, li) {
                              var $a = $(li).children('a').clone();
                              $a.attr("href", "#");
                              if(n != 0)
                                $lst.prepend(' <span class="te_main_a">/ </span> ', $a);
                        });
                        $('.te_breadcrumb_ctg').html( $lst.prepend('<a href="/shop">Shop</a>') );
                        $(this).css("display", "none")
                        $(this).parent().parent(".t_custom_subctg").css("overflow-y", "auto");
                    });
                })
            }
        })
        $(document).on('click',".ctg_arrow",function(ev) {
            $(this).parents("#custom_menu").animate({
                width: "500px",
            });
        });
        $(document).on('click',"#te_main_ul >#custom_menu_li >#custom_recursive >.te_prent_ctg_heading", function(ev) {
            $(this).parents("#custom_menu").stop().animate({
                width: "250px",
            });
        });
        $(document).on('click',"#custom_menu > li > ul.t_custom_subctg > .te_prent_ctg_heading",function() {
            $(this).parents("#custom_menu").css("overflow-y", "auto");
        })
        if ($(window).width() <= 1200) {
            $("#custom_menu li").each(function() {
                $('.ctg_arrow').css("display","none");
                $('.te_main_a').css("width","100%");
            });
        }
        if($(window).width() < 768){
            $("#te_main_ul").css("max-width","100%");
            $("#custom_menu").css({
                "left": "0",
                "right": "0",
                "width": "100%",
            });
        }
        //Changed search form action in theme's search when website search is installed
        if ($("body").find(".website_search_form_main").length > 0) {
            $(".te_header_search,.te_searchform__popup").each(function() {
                $(this).find("form").attr("action", "/search-result");
            })
            $(".website_search_form_main").html("");
        }
        //Recently viewed title
        if ($('#carousel_recently_view .carousel-inner .img_hover').length >= 1) {
            $('.te_product_recent_h2').css('display', 'block')
        }
        //expertise progress bar
        $('.progress').each(function() {
            var area_val = $(this).find('.progress-bar').attr("aria-valuenow")
            $(this).find('.progress-bar').css("max-width", area_val + "%")
        })
        //Remove images in extra menu
        $("li.o_extra_menu_items").find("img").removeAttr("src alt");

        // if slider then active first slide
        if ($('.recommended_product_slider_main').length) {
            $(".theme_carousel_common").each(function() {
                $(this).find(".carousel-item").first().addClass("active");
            })
        }
        // Change in carousel to display two slide
        $('.theme_carousel_common .carousel-item').each(function() {
            var next = $(this).next();
            if (!next.length) {
                next = $(this).siblings(':first');
            }
            next.children(':first-child').clone().appendTo($(this));
        });
        // quantity design in cart lines when promotion app installed
        $(".te_cart_table .css_quantity > span").siblings("div").css("display", "none")
        // Portal script
        if ($('div').hasClass('o_portal_my_home')) {
            if (!$('a').hasClass('list-group-item')) {
                $(".page-header").css({
                    'display': 'none'
                })
            }
        }

        /** On click selected input, filter will be clear*/
        $('.nav-item input[type="checkbox"]').click(function(){
            if($(this).prop("checked") == false){
                var self = $(this);
                var attr_value;
                if (self.parent("label").hasClass("css_attribute_color")) {
                    attr_value = self.parent("label").siblings(".te_color-name").html();
                    if(attr_value) {
                        attr_value = attr_value.toLowerCase();
                        attr_value = attr_value.replace(/(^\s+|[^a-zA-Z0-9 ]+|\s+$)/g,"");
                        attr_value = attr_value.replace(/\s+/g, "-");
                    }
                } else {
                    attr_value = self.siblings("span").html();
                    if(attr_value) {
                        attr_value = attr_value.toLowerCase();
                        attr_value = attr_value.replace(/(^\s+|[^a-zA-Z0-9 ]+|\s+$)/g,"");
                        attr_value = attr_value.replace(/\s+/g, "-");
                    }
                }
                $('.te_view_all_filter_div .te_view_all_filter_inner').find('.te_clear_attr_a.'+attr_value).trigger('click');
            }
        });
        $( "select" ).change(function () {
            $(this).find("option:selected").each(function() {
                var attr_value = $(this).parents('.nav-item').find('.te_clear_all_variant').attr('attribute-name');
                if(!$(this).text()) {
                    $('.te_view_all_filter_div .te_view_all_filter_inner').find('.te_clear_attr_a.'+attr_value).trigger('click');
                }
            });
        });
        var product_detail = new sAnimations.registry.product_detail();
        product_detail.productGallery();
    })


    //------------------------------------------
    // 07. Compare short name
    //------------------------------------------
    $(document).ready(function(){
        var maxLength = 26;
        var number_compare_item = $("#o_comparelist_table").find('tr:first').find('td').length;
        if(number_compare_item == 4)
        {
            maxLength = 35;
        }
        else if(number_compare_item == 3)
        {
            maxLength = 50;
        }

        var ellipsestext = "...";
        $(".more").each(function(){
            var myStr = $(this).text();
            if($.trim(myStr).length > maxLength){
                var newStr = myStr.substring(0, maxLength);
                var html = newStr + '<span class="moreellipses">' + ellipsestext+ '</span>';
                $(this).html(html);
            }
        });

        $("#myCarousel_banner_prod_slider").find(".a-submit").click(function (event) {
            sale._onClickSubmit(event)
        });

        var myCarousel_acce_full = $('.accessory_product_main.full-width .owl-carousel, .alternative_product_main.full-width .owl-carousel').owlCarousel({
            loop: false,
            rewind: true,
            margin: 10,
            lazyLoad:true,
            nav: true,
            dots: false,
            autoplay: true,
            autoplayTimeout: 4000,
            navText : ['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
            autoplayHoverPause:true,
            items: 4,
            responsive: {
                0: {
                    items: 1,
                },
                576: {
                    items: 2,
                },
                991: {
                    items: 3,
                },
                1200: {
                    items: 4,
                }
            }
        });

        var myCarousel_acce_prod = $('.accessory_product_main .owl-carousel, .alternative_product_main .owl-carousel').owlCarousel({
            loop: false,
            rewind: true,
            margin: 10,
            lazyLoad:true,
            nav: true,
            dots: false,
            autoplay: true,
            autoplayTimeout: 4000,
            navText : ['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
            autoplayHoverPause:true,
            items: 2,
            responsive: {
                0: {
                    items: 1,
                },
                576: {
                    items: 2,
                }
            }
        });
    });

    $(".o_portal_my_doc_table tr").click(function(){
      window.location = $(this).find('td > a').attr("href");
      return false;
    });

    /** Login / Signup Popup **/
    $(document).on('click', '.te_user_account_icon, .te_signin', function(){
        $("#loginRegisterPopup").modal();
        $('body').find('.modal-backdrop').css('position','relative');
    });

    $("#loginRegisterPopup .oe_reset_password_form").hide();
    $("#loginRegisterPopup .open_reset_password").click(function(){
        $("#loginRegisterPopup .oe_login_form").hide();
        $("#loginRegisterPopup .oe_reset_password_form").show();
    });
    $("#loginRegisterPopup .back_login").click(function(){
        $("#loginRegisterPopup .oe_reset_password_form").hide();
        $("#loginRegisterPopup .oe_login_form").show();
    });

    publicWidget.registry.productsRecentlyViewedSnippet.include({
        /*
         Adds the stock checking to the regular _render method
        @override
        */
        _render: function (){
            this._super.apply(this, arguments);
            var r_name = $("#te_rect_cnt").text();
            $('.te_recently_viewed').find('h6').each(function(){
                $(this).addClass("te_rect_name")
                if(r_name == 2) {
                    $('h6.card-title').addClass('te_2_line');
                }
                if(r_name == 3) {
                    $('h6.card-title').addClass('te_3_line');
                }
            });
        },
    });



    sAnimations.registry.reset_password_popup = sAnimations.Class.extend({
        selector: "#wrapwrap",
        start: function () {
            self = this;
            self.resetPassword();
            self.customerLogin();
            self.customerRegistration();
            self.selectProductTab();
        },
        resetPassword: function(){
            $("#loginRegisterPopup .oe_reset_password_form").submit(function(e) {
                var $form = $('#loginRegisterPopup .oe_reset_password_form');
                e.preventDefault();
                var url = '/web/reset_password?'+$form.serialize();
                    $.ajax({
                    url: url,
                    type: 'POST',
                    success: function(data) {
                        var oe_reset_password_form_error = $(data).find('.te_reset_password_form').find('.alert.alert-danger').html();
                        var oe_reset_password_form_success  = $(data).find('main .oe_website_login_container').find('.alert.alert-success').html();
                        if($(data).find('.te_reset_password_form').find('.alert.alert-danger').length) {
                            $("#loginRegisterPopup .oe_reset_password_form .te_error-success").replaceWith("<div class='te_error-success alert alert-danger'>" + oe_reset_password_form_error + "</div>");
                        }
                        if($(data).find('main .oe_website_login_container').find('.alert.alert-success').length) {
                            $("#loginRegisterPopup .oe_reset_password_form .te_error-success").replaceWith("<div class='te_error-success alert alert-success'>" + oe_reset_password_form_success + "</div>");
                        }
                    }
                });
            });
        },

        customerLogin: function(){
            $("#loginRegisterPopup .oe_login_form").submit(function(e) {
                var $form = $('#loginRegisterPopup .oe_login_form');
                e.preventDefault();
                var url = '/web/login?'+$form.serialize();
                    $.ajax({
                    url: url,
                    type: 'POST',
                    success: function(data) {
                        var oe_reset_password_form_error = $(data).find('.oe_login_form').find('.alert.alert-danger').html();
                        if($(data).find('.oe_login_form').find('.alert.alert-danger').length) {
                            $("#loginRegisterPopup .oe_login_form .te_error-success").replaceWith("<div class='te_error-success alert alert-danger'>" + oe_reset_password_form_error + "</div>");
                        } else {
                            if (data.includes('"is_admin": true')) {
                                $(location).attr('href', '/web');
                            } else {
                                $(location).attr('href', '/my');
                            }
                        }
                    }
                });
            });
        },

        customerRegistration: function(){
            $("#loginRegisterPopup .oe_signup_form_ept").submit(function(e) {
                var $form = $('#loginRegisterPopup .oe_signup_form_ept');
                e.preventDefault();
                var url = '/web/signup?'+$form.serialize();
                    $.ajax({
                    url: url,
                    type: 'POST',
                    success: function(data) {
                        var oe_reset_password_form_error = $(data).find('.oe_signup_form').find('.alert.alert-danger').html();
                        if($(data).find('.oe_signup_form').find('.alert.alert-danger').length) {
                            $("#loginRegisterPopup .oe_signup_form_ept .te_error-success").replaceWith("<div class='te_error-success alert alert-danger'>" + oe_reset_password_form_error + "</div>");
                        } else {
                            $(location).attr('href', '/send/confirmation/mail')
                        }
                    }
                });
            });
        },

        selectProductTab: function(){
            if ($('.specification_products_tab').length < 1) {
                $('#te_product_tabs').find('li:first-child').find('.nav-link').addClass('active');
                var firstAttr = $('#te_product_tabs').find('li:first-child').find('.nav-link').attr('aria-controls');
                $('.tabs_container_main .product-body .tab-pane').removeClass('active show');
                $('#'+ firstAttr).addClass('active show');
            }
        },
    });

    $('.te_banner_slider_content').owlCarousel({
        loop: true,
        nav: true,
        dots: false,
        lazyLoad:true,
        navText : ['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
        autoplay: true,
        autoplayTimeout: 4000,
        autoplayHoverPause:true,
        items: 1,
        responsive: {
            0: {
                items: 1,
            },
            576: {
                items: 1,
            },
        },
    });


});
