odoo.define('quick_order.main', function (require) {
  "use strict";
  /* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
  /* See LICENSE file for full copyright and licensing details. */
  var ajax = require('web.ajax');
  var core = require('web.core');
  var QWeb = core.qweb;
  var xml_load = ajax.loadXML(
      '/website_sale_stock/static/src/xml/website_sale_stock_product_availability.xml',
      QWeb
  );
  require('web.dom_ready');

 $("#table_order").find(".main_add_to_cart").find("tr").each(function() {
   var $el = $(this).find("#qunatity");
   checkAvailability($el);
 });


  function checkAvailability (product_ids) {
    product_ids.each(function(){
      var $el = $(this);
      var config = {};
      config.product_id = parseInt($el.parents('tr').attr('item_id'));
      config.add_qty = parseInt($el.val());
      config.product_template_id = parseInt($el.parents('tr').attr('temp_id'));
      config.combination = [];
      config.pricelist_id = false;
      ajax.jsonRpc('/sale/get_combination_info_website', 'call', config)
      .then(function(combination){
        xml_load.then(function () {
            var $message = $(QWeb.render(
                'website_sale_stock.product_availability',
                combination
              ));
            var $parent = $el.parents('.slid-up-table').find('.quick_order_stock');
            $parent.empty();
            $parent.append($message);
        });
      })
    })
  };



  var _t = core._t;
  var val = '';
  var ref;
  var doneTypingInterval = 500;
  var typingTimer;


  function getPrice(){
    var $ele = $("#lanfConfig");
    var data = {
      "dec_point": $ele.attr("decimal_point"),
      "thousands_sep": $ele.attr("thousands_sep"),
      "grouping": $ele.attr("grouping")
    };
    return data;
  }

  var langConfig = getPrice();

  function changePriceDec(data){
    try {
      var price = data.split(langConfig.thousands_sep).join("");
      price = price.replace(langConfig.dec_point, '.');
      price = parseFloat(price);

      return price;

    } catch (e) {
      console.log(e);
      return e;
    }

  };



  function numberWithCommas(price) {
    price = parseFloat(price).toFixed(2);
    var array = price.toString().split(".");
    price = "";
    var lastDigit = array[array.length-1];
    var firstDigit = array[0];

    var sparatorPosition = JSON.parse(langConfig.grouping);

    sparatorPosition = sparatorPosition[0];
    firstDigit = firstDigit.split("");
    var x = 0
    for(var i = firstDigit.length-1; i>=0; i--){
      x++;
      if(x==sparatorPosition && i != 0){
        x=0;
        price = price.concat(firstDigit[i]).concat(langConfig.thousands_sep);
      }else{
        price = price.concat(firstDigit[i]);
      }
    }
    price = price.split("").reverse().join("");
    price = price.concat(langConfig.dec_point).concat(lastDigit);
    return price;
  };


  /* Get Sum of sub total in table and also get the total quantity */
  function find_sum() {
    var total_rs = 0;
    var total_qty = 0;
    $(".main_add_to_cart tr").each(function(i) {
      var fin = parseInt($(this).find('#qunatity').val())
      if( fin > 0){
        total_qty += parseInt(($(this).find('#qunatity').val()).replace(',' , ''));
        total_rs += changePriceDec($(this).find("#sub_total").find('.oe_currency_value').text());
      }})
      $('.total .oe_currency_value').empty();
      $('.total p').empty();
      $('.total .oe_currency_value').text(numberWithCommas(total_rs));
      $('.total p').text('Total Qty : ' + total_qty);
      var href = window.location.pathname;
      if(href.includes('/quickorder/shoppinglist')){
          total_for_cart(total_rs, total_qty);
      }
  }
window.onbeforeunload = function() { return };

  $(document).ready(function(){
    $('.hover-single-fa').hover(function(){
      $('#ul_append').toggleClass('show-shopping-list');
    })
    $('#ul_append').hover(function(){
      $('#ul_append').toggleClass('delay-shopping-list');
    })
  })

/* After submit variants need to clear and count table value and other operation on page */
  function submit_variants(){
    $('tr').css("border-left","0px solid white");
    $(".modal").modal('hide');
    find_sum();
    get_data_clear();
    $('#create_order').show();
  }



/* Get total price and quantity when change on a single row of Order List quantity */
  function total_for_cart(rs, qty) {
    var id = $('.main_add_to_cart').closest('.inner').find('.oe-get_shopping_list').attr('ids');
    $('.dropdown-hover li').each(function(i){
       var li_id = $(this).attr('value');
       if(id==li_id){
         var div = $(this).find('div[class="row"]')
         div.children('div').eq(0).text(qty+' items');
        $(this).find('.li-right .oe_currency_value').text(numberWithCommas(rs.toFixed(2)));
       }
    });
  }

/* Clear tabales, messages and manage other functionality of web pages */
  function get_data_clear(){
    $("#order_quick_table").show();
    $('.alert-success').hide();
    $('#error_404').hide();
    $('#no_products').hide();
    $('#clear_all').show();
  }

  function set_sub_total(val) {
    var selector = 'tr[item_id="'+val+'"]';
    var no = parseInt($(selector).find('input[type="number"]').val())+1;
    $(selector).find('input[type="number"]').val(no);
    var sub_total = parseFloat($(selector).find("#lst_price .oe_currency_value").text()) * no;
    $(selector).find("#sub_total .oe_currency_value").text(sub_total.toFixed(2));
  }

  function hide_table(message) {
    $('.alert-success').empty().append('<p>'+message+'</p>').show();
    $('.main_add_to_cart').empty();
    $('#order_quick_table').hide();
    $('#clear_all').hide();
  }


   function get_total_order() {
     var order = [];
     $(".main_add_to_cart tr").each(function(i) {
       var quantity = $(this).find('#qunatity').val();
       if(quantity > 0){
         order.push({"id": parseInt($(this).attr('item_id')), "quantity": parseFloat(quantity)});
       }
     })
     return order
   }

   $('.container-text').each(function () {
      var page_refferance  = this;
      find_sum();
      $(".modal-setName").keydown(function(e){
          if(e.which === 13){
              $("#submit_shopping_cart").click();
          }
      });
      $(page_refferance).on('click','.deselect-variants input[type="checkbox"]', function(e){
        var id = $('.variants-c input[type="checkbox"]');
        if (id.length == $('.variants-c').find('input[type="checkbox"]:checked').length){
          $('.select_all_variants input[type="checkbox"]').prop('checked', true);
        }
        else{
          $('.select_all_variants input[type="checkbox"]').prop('checked', false);
        }
      })
  /* delete Quick Order Lists and Shopping Lists baesd on requirements */
      $(page_refferance).on('click','.delete_product', function(e) {
        e.preventDefault()
        var att = $(this);
        delete_product_action(att)
      });


/* Close all opend modal */
      $(page_refferance).on('click',".close-m", function(e) {
          $('tr').css("border-left","white");
          $(".modal").modal('hide');
      })

/* Add prodtuct templates into Quick Order List */
      $(page_refferance).on('click',"#addToList", function(e) {
          var id = []
          $(".variants").each(function(i) {
            var bool = $(this).find("input[type='checkbox']").is(':checked');
            if (bool){ id.push($(this).attr('data-oe-id')); }
          })
          if(id.length > 0){
            ajax.jsonRpc('/quickorder/addproducts', 'call',{"product_ids" : id})
              .then(function(data){
                  if(data.delete_template_row){
                    $(".modal").modal('hide');
                    ref.find('.slid-up-table').slideUp(300, function(){
                      ref.remove();
                      if ($("#tableitems").find('.clickable').length <= 1){
                        var url = '/quickorder/quicksearch?search='+$('#search_quick_render .oe_search_box').val();
                        get_table(url);
                      }
                    });
                  }
                  var $template = $($.parseHTML(data.template));
                  checkAvailability($template.find("input[type='number']"));
                  $('.main_add_to_cart').append($template);
                  submit_variants();
                })

          }
          else{ $('.variants-error').css('display', 'block').hide().fadeIn('slow');setTimeout(function(){$('.variants-error').css('display', 'none'); },3000); }
        })

/* Add prodtuct templates into Shopping List */
        $(page_refferance).on('click', '#submit_shopping_cart', function(e){
          var id  = $(".main_add_to_cart tr:first").attr('data_id');
          name = $("#shopping_list_name").val();
          var bool = true;
          if ($(this).text() == 'Submit' && (name.length <=0 || name=='')){
            $('.null_name_shopping_list').show().delay(3000).hide(1);
            return false;
          }
          if (name.length <=0 || name==''){
            bool = false;
          }
          if (id > 0){
            ajax.jsonRpc('/quickorder/addshoppinglist', 'call',{"id" : id, "create": bool, "name" : name, "list_id" : val})
              .then(function(data){
                if (data.route == true){
                     $("#shopping_list_name").val('');
                     window.location.pathname=data.url;
                }
              })
              $(".modal").modal('hide');
          }
        })

/* Pop up for creating a new Shopping List and add product to exixting Shopping List */
        $(page_refferance).on('click','.create_new_list', function(e){
          val = '';
          if ($(this).hasClass("create")) {
             $(".modal-setName").modal('show');
          } else {
            val = $(this).attr('value');
            $('.modal-confirm').modal('show');
          }
        })



/* Search Product template when user enter text in text-box */
         $(page_refferance).on('keyup','#search_quick_render .oe_search_box', function(e) {
           var $ref = $(this);
           clearTimeout(typingTimer);
           typingTimer = setTimeout(function(){
             var url = '/quickorder/quicksearch?search='+$ref.val();
             get_table(url);
           }, doneTypingInterval);
         })

/* Click event on product template row for creating a quick order list */
         $(page_refferance).on('click',"#add_in_orderline", function(e) {
          $(".modal").modal('hide');
          $('.load-search').css("display","flex");

           var referr = $(this).parents(".clickable");
           ref = $(this).parents(".clickable");
           var bool = true;
           bool = typeof $(e.target).parents(".clickable").parents('a').attr('href') != 'undefined' ? false : true;
           if (bool){
             bool = typeof $(e.target).parents(".clickable").attr('href') != 'undefined' ? false : true;
           }
           if(bool){
             $(this).parents(".clickable").css("border-left","3px solid #428bca");
             var id = $(this).parents(".clickable").attr("data-oe-id");
             $.get('/quickorder/getvariants', {"product_id" : id})
               .done(function(data,textStatus, xhr) {
                   if(xhr.status == 211){
                     referr.find('.slid-up-table').slideUp(300, function(){
                       referr.remove();
                       $('tr').css("border-left","0px solid white");
                       find_sum();
                       get_data_clear();
                     });
                      var $item = $($.parseHTML(data));
                      checkAvailability($item.find("#qunatity"));
                      $('.main_add_to_cart').append($item);
                      if ($("#tableitems").find('.clickable').length <= 1){
                        get_table('/quickorder/quicksearch');
                      }
                   }
                   else{
                     $("#row_select_model").html(data);
                     $('.load-search').css("display","none");
                     $(".modal-variants").modal('show');
                   }
		              $('.load-search').css("display","none");
                  $('#create_order').show();

                 })
           }
         });

         function get_table(url){
             $('.load-search').css("display","flex");
             $.get(url, {"key_press" : true})
               .done(function(data){
                 $('#search_table_render_here').empty().append(data);
                  var prev = $('.pager-page').html();

                  var next = $('.pager-page').find('ul li:last-child').html();
                 $('#top_pager').empty().append(prev);
                 $('#top_pager ul li:not(:first):not(:last)').remove();
                 $("#top_pager ul li:first").find('i').removeClass('fa-caret-left').addClass('fa-arrow-left');
                 $("#top_pager ul li:last").find('i').removeClass('fa-caret-right').addClass('fa-arrow-right');
                 $("#top_pager ul li:first").find('a').addClass('left-prev-link page-link');
                 $("#top_pager ul li:last").find('a').addClass('right-next-link page-link');
               })
         }
        //  get_table('/quickorder/quicksearch');

         $(page_refferance).on('click','.open-e-sp-name', function(event){
           $('.e-sp-up-name').parent().parent('.modal-body').find('p').hide();
           $('.e-sp-up-name').attr('no',$(this).parent().attr('no'));
           $('#myModal').modal('show');
         })

         $(page_refferance).on('click', '.e-sp-up-name', function(e){
           var name = $('.e-sp-l-name').val();
           var id = $(this).attr('no');
           if (typeof name == undefined || name == ''){
             $(this).parent().parent('.modal-body').find('p').show();
             return;
           }
           ajax.jsonRpc('/quickorder/update/name', 'call',{"s_name":name, "id":id})
             .then(function(data){
               if (data.success == "ok"){
                 $("#"+id).find('h4').html(data.name);
               }
               $('#myModal').modal('hide');
             })

         })

         $(page_refferance).on('click','.pager-page ul li, #top_pager ul li', function(event){
           if ($(this).prop('class') == 'disabled'){
             event.preventDefault();
           }
         })

         $(page_refferance).on('click', '.select_all_variants input', function(e){
             if (! $(this).is(':checked')){
               $('.variants-c .variants').each(function(index){
                 $(this).find('input[type = "checkbox"]').prop('checked', false);
               })
             }
             else {
               $('.variants-c .variants').each(function(index){
                 $(this).find('input[type = "checkbox"]').prop('checked', true);
               })
             }
         })

         $(page_refferance).on('click', '#refresh_table', function(e){
           get_table('/quickorder/quicksearch');
           $('input[name="search"]').val('');
         })
/* Remove the Quick Order List */
         $(page_refferance).on('click',"#clear_all", function(e)  {
           e.preventDefault();
           var rowCount = $('#table_order tr').length;
           if(rowCount>0){
             ajax.jsonRpc('/quickorder/deleteallproduct', 'call',{})
               .then(function(data){
                 hide_table('<p>'+data.success+'</p>');
                 get_table('/quickorder/quicksearch');
               })
            }
         })

/* Create Shopping List */
         $(page_refferance).on('click',"#create_order", function(e) {
           var el=$(this);
           var href = window.location.pathname;
           var id = 0;
           var order = get_total_order();
           var bool = false;
           if(href.includes('/quickorder/shoppinglist')){
             bool = true;
             id = $('.main_add_to_cart').closest('.inner').find('.oe-get_shopping_list').attr('ids');
           }
           else{
             id = $('.main_add_to_cart').find('tr:first').attr('data_id');
             }
           if (order.length > 0){
             ajax.jsonRpc('/quickorder/createorder', 'call',{"order_now" : order, "id" : id})
               .then(function(data){
                    $(this).remove();
                    window.location.pathname = "/shop/cart";
                })
            }
           else{
             $('.alert-success').empty().append('<p style="color: #728794;">Total quantity of products is 0</p>').show().delay(5000).hide(1);
           }
       })

/* Add products into Order Cart from Shopping Lits */
       $(page_refferance).on('click',".fun-create_order",function(e){
         var div  = $(this).parents('.outer')
         var id = div.attr('id');
         var order_now = [];
         if ($('.main_add_to_cart').find('tr').length > 0){
           order_now = get_total_order();
         }
         ajax.jsonRpc('/quickorder/shoppinglist/curd','call', {'shopping_id': id, 'order_now': order_now})
         .then(function(success){
           if(success.error){
             $('.alert-success').empty().append('<p>'+success.error+'</p>').show();
             $('.outer:nth-child(2)').remove();
             $('#ul_append').append('<li style="text-align:center;"><label>Your Shopping List is empty</label></li>');
           }
           else{
             $('li[value="'+id+'"]').closest('li').remove();
             div.slideUp(300, function(){
               window.location.pathname = '/shop/cart';
             })
           }
         })
       });

  /* Get all and a single Shopping List baesd on id */
       $(page_refferance).on('click', '.oe-get_shopping_list', function(e){
         var ref = $(this);
         if (! $(e.target).hasClass("fun") && ! $(e.target).hasClass("fa-pencil-square-o")){
           var id = ref.attr('ids');
           var len = "#"+id+" #table_added";
           if ($(len).length > 0){
             $('.shopping-id').slideUp(500);
             $(".chevron-up").hide();
             $(".chevron-down").show();
             ref.find(".chevron-down").show();
             $('.shopping-id').empty();
           }
           else{
                $.get('/quickorder/shoppinglist', {"id" : id}).done(function(data){ })
                .then(function(success){
                  $('.shopping-id').slideUp(500).empty();
                  $('div[render="'+id+'"]').html(success);
                  $('div[render="'+id+'"]').slideDown(500);
                  $(".chevron-up").hide();
                  $(".chevron-down").show();
                  ref.find(".chevron-down").hide();
                  ref.find(".chevron-up").show();
                  find_sum();
                })
           }
         }
       });

  /* Remove all and a single Shopping List baesd on id */
       $(page_refferance).on('click','.delete-list', function(e){
         e.preventDefault();
         var div  = $(this).parents('.outer');
         var id = div.attr('id');
         var location = window.location.pathname;
         if(id){
           $.get('/quickorder/shoppinglist/delete',{'shopping_id': id})
             .then(function(response){
               $('li[value="'+id+'"]').closest('li').remove();
               div.slideUp(300, function(){
               div.remove();
               if(! response.includes('{"')){
                   $('.outer').append("<div class='inner'>"+response+"</div>");
                   $('#ul_append').append('<li style="text-align:center;"><label>Your Shopping List is empty</label></li>');
               }
               else if(location.length > 24){
                 window.location.href = '/quickorder/shoppinglist/';
               }
             })
            })
          }
        });

        $(page_refferance).on('click', '.modal', function(e){
          if ($(e.target).attr('class') == 'modal modal-variants fade modal_shown'){
            $('.clickable').css("border-left","0px solid white");
          }
        })

/* Plus and Minus button click on tables */
        $(page_refferance).on('click','.add-product', function(e){
          e.preventDefault();
          var no  = parseFloat($(this).closest("tr").find('#qunatity').val());
          if ($(this).attr("id") == 'plus'){
            no += 1;
          }
          if ($(this).attr("id") == 'minus' && no > 0){
            no -= 1;
          }
          checker_for_quantity(no, $(this));
        });

/* Count total quantity and price when change on user enter the quantity */
      $(page_refferance).on('keyup',"#qunatity", function(e) {
          var no = $(this).val();
          checker_for_quantity(no, $(this));
       })

   })

   function checker_for_quantity(ref, reff){
     if (ref == 0){
       delete_product_action(reff)
     }
     else{
       update_quanity(ref, reff);
     }
   }

   function update_quanity(qty, p_this){
     var ref = p_this.parents('tr');
     var line_id = parseInt(ref.attr('line_id'));
     $.get('/quickorder/shoppinglist/update/quantity',{
       'qty': qty,
       'line_id': line_id
     }).then(function(res){
       checkAvailability(p_this);
       res = JSON.parse(res);
       var closetTr = p_this.closest("tr");
       closetTr.find("#qunatity").val(qty);
       var sub_total = changePriceDec(String(res.price).replace(".", langConfig.dec_point)) * qty;
       closetTr.find("#lst_price .oe_currency_value").text(numberWithCommas(res.price.toFixed(2)));
       closetTr.find("#sub_total .oe_currency_value").text(numberWithCommas(sub_total.toFixed(2)));
       find_sum();
     });
   }


   function delete_product_action(att){
     var href = window.location.pathname;
     if(href.includes('/quickorder/shoppinglist')){
       var product_id = att.parents('tr').attr('line_id');
       var shopping_id = att.parents('.outer').attr('id');
       $.get('/quickorder/shoppinglist/delete',{'product_id': product_id, 'shopping_id':shopping_id})
         .then(function(data){
           att.closest("tr").find('.slid-up-table').slideUp(300, function(){
           att.closest("tr").remove();
           find_sum();
           var rowCount = $('#table_order tr').length;
           if(rowCount<2){
             total_for_cart(0,0);
             $('#table_added').hide();
           }
         });
       })
     }
     else{
       ajax.jsonRpc('/quickorder/deleteproduct', 'call',{"item_id" : att.closest('tr').attr('line_id')})
         .then(function(data){
             att.closest("tr").find('.slid-up-table').slideUp(300,function(){
               att.closest("tr").remove();
               find_sum();
               if(data.delete == true){
                 $('#order_quick_table').hide();
                 $('#clear_all').hide();
                 $('.alert-success').empty().append('<p>'+data.success+'</p>').show();
               }
             });
         })
     }
   }


});
