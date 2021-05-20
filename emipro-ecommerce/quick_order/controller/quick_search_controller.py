# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo.http import route, request, Controller, Response
from odoo.addons.portal.controllers.portal import CustomerPortal
import werkzeug
import json
import logging
from odoo.exceptions import Warning
_log = logging.getLogger(__name__)
MAX_PAGE_SIZE_PAGINATION = 10


class QuickSearchConroller(Controller):

###########################################################
## Change currency according as from_currency to to_currency
############################################################
    def compute_currency(self, price):
        order = request.website.sale_get_order(force_create=1)
        from_currency = order.company_id.currency_id
        to_currency = order.pricelist_id.currency_id
        return round(from_currency.compute(price, to_currency), 2)


    def variants_availability(self):
        quick_order = request.env['quick.order'].search([('state','=','draft'), ('user_id', '=', request._uid)])

        return [id.product_id.id for id in quick_order.quick_order_line]

    def shopping_list_availability(self, shopping_list):
        if len(shopping_list)==1:
            return [id.product_id.id for id in shopping_list.quick_order_line]
        return []
###########################################################################
## Get main page, product Order List, searching logic, pagination and
## domain filter for product template that are already in Order List.
###########################################################################
    @route(['/quickorder','/quickorder/page/<page_no>','/quickorder/quicksearch'], type = 'http', auth = 'public', website = True)
    def get_quick_search_form(self,search='', page_no=1, key_press=False, **kw):
        if request.website.is_public_user():
            return request.render('quick_order.quick_order_public_user_sugges',{})
        order_quick = request.env["quick.order"].search([('user_id', '=', request._uid), ('state', '=', 'draft')])
        domain = [('product_variant_ids.id', 'not in', self.variants_availability()),('website_published','=', True)]
        error = ''
        s_error = ''
        prev_str = request.session.get('previous_search_string')
        not_click_event = request.httprequest.full_path.startswith('/quickorder/quicksearch')
        if not (prev_str == search) and not not_click_event:
            if search:
                url = '/quickorder?search='+search
            else:
                url = '/quickorder'
            request.session['previous_search_string'] = search
            return werkzeug.utils.redirect(url)
        if search:
            for srch in search.split(" "):
                domain += [
                            '|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
                            ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)
                         ]
        page_no = int(page_no)
        offset = (page_no-1)*MAX_PAGE_SIZE_PAGINATION
        prod = request.env['product.template'].search(domain)
        if len(prod) <= 0:
            s_error = request.env['quick.order.message'].search([],limit=1)
            s_error = s_error.message_on_product_search
        length = len(prod)//MAX_PAGE_SIZE_PAGINATION
        if len(prod)%MAX_PAGE_SIZE_PAGINATION == 0:
            length = length
        else:
            length = length+1
        pager = request.website.pager(url="/quickorder", total=len(prod), page=page_no, step=MAX_PAGE_SIZE_PAGINATION, scope=5, url_args={"search": search})
        if len(order_quick.quick_order_line) <= 0:
            error = request.env['quick.order.message'].search([],limit=1)
            error = error.message_on_empty_order_list
        shopping_list = request.env["quick.order"].search([('user_id', '=', request._uid),  ('state', '=', 'shopping_list')])
        response = {
            'products' : prod[offset : offset+MAX_PAGE_SIZE_PAGINATION],
            'pager' : pager,
            'order_quicks' : order_quick.quick_order_line,
            'id' : order_quick.id,
            'shopping_list' : shopping_list,
            'error' : {'error': error, 's_error': s_error},
            'compute_currency' : self.compute_currency,
            'product_r': self.variants_availability()
            }
        if not not_click_event:
            request.session['previous_search_string'] = search
        if search:
            response['search']=search
        if key_press:
            return request.render('quick_order.main_table_data', response)
        return request.render('quick_order.quick_search_main_template', response)

###################################################################################
## Get the all variants of product template if exixts else submit into Order List
###################################################################################
    @route(['/quickorder/getvariants'], type = "http", auth = "user", website = True)
    def get_variants(self, product_id, **kw):
        product_id = int(product_id)
        products = None
        total_valid =[]
        prod = request.env['product.template'].sudo().browse(product_id)
        not_id = prod.product_variant_ids.ids
        user_exists = request.env['quick.order'].search([('user_id', '=', request._uid),('state', '=', 'draft')])
        if len(prod.product_variant_ids) == 1:
            if user_exists:
                products_exists = self.variants_availability()
                if prod.product_variant_ids.id not in products_exists:
                    user_exists.quick_order_line = [(0, 0, {"product_id" : prod.product_variant_ids.id})]
            elif not user_exists:
                user_exists = request.env['quick.order'].create({
                                            "quick_order_line": [(0, 0, {"product_id" : prod.product_variant_ids.id})]
                                            })
            products = prod.product_variant_ids.ids
            return Response(request.env['ir.ui.view'].render_template('quick_order.add_to_cart_mutliple_body',{'order_quicks' : user_exists.quick_order_line, 'id':user_exists.id, 'compute_currency' : self.compute_currency, 'product_r': products}),content_type='text/html;charset=utf-8',status=211)
        if not prod.product_variant_ids:
            return Response({'error' : "No variants found"}, content_type='application/json',status=500)
        if user_exists:
            not_id = list(set(prod.product_variant_ids.filtered(lambda x: x.product_tmpl_id._is_combination_possible(x.product_template_attribute_value_ids)).ids)-set(self.variants_availability()))
        return request.render("quick_order.row_select_model", {"docs" : prod, "not_id" : not_id})


##########################################################################
## Submit the variants of product template into Quick Order List
##########################################################################
    @route(['/quickorder/addproducts'], methods=['POST'], type = "json", auth = "user", website = True)
    def add_products(self, **kw):
        product_ids = kw.get('product_ids')
        products = None
        total_valid = []
        delete_template_row = False
        template = ''
        product_r = []
        try :
            if len(product_ids):
                user_exists = request.env['quick.order'].search([('user_id', '=', request._uid),('state', '=', 'draft')])
                if user_exists:
                    products_exists = self.variants_availability()
                    for product_id in product_ids:
                        if int(product_id) not in products_exists:
                            user_exists.quick_order_line= [(0,0,{"product_id" : int(product_id)})]
                            total_valid.append(int(product_id))
                    product_r = total_valid
                elif not user_exists:
                    ids = [(0,0, {"product_id" : int(id)}) for id in product_ids]
                    product_r = [int(id) for id in product_ids]
                    user_exists = request.env['quick.order'].create({
                        'quick_order_line': ids
                    })
                    products = user_exists.quick_order_line
                user_exists = request.env['quick.order'].search([('user_id', '=', request._uid),('state', '=', 'draft')])
                if total_valid:
                    products = user_exists.quick_order_line
                if products:
                    template = request.env['ir.ui.view'].sudo().render_template('quick_order.add_to_cart_mutliple_body',{'order_quicks' : products,'id' :user_exists.id, 'compute_currency' : self.compute_currency, 'product_r':  product_r})
                product_template = request.env['product.template'].search([('product_variant_ids.id', '=', int(product_ids[0]))])
                if product_template:
                    combination = set(product_template.product_variant_ids.filtered(lambda x: x.product_tmpl_id._is_combination_possible(x.product_template_attribute_value_ids)).ids)
                    delete_template_row = (set(self.variants_availability()) > combination) or (set(self.variants_availability()) == combination)
                return {
                    "template" : template,
                    "delete_template_row" : delete_template_row
                    }
        except Exception as e:
            raise Warning('Product id is invalid need int found String {}.'.format(e))
        return Response({'error' : "error"}, content_type='application/json',status=500)

########################################################################
## Delete the products from Quick Order List baesd on product id
########################################################################
    @route(['/quickorder/deleteproduct'], type = "json", auth = "user", website = True)
    def delete_product(self, item_id='', **kw):
        success = ''
        delete = False
        if item_id:
            user_exists = request.env['quick.order'].search([('user_id', '=', request._uid),('state','=', 'draft')])
            if user_exists:
                user_exists.write({"quick_order_line":[(2, int(item_id))]})
                if not len(user_exists.quick_order_line):
                    success  = request.env['quick.order.message'].search([], limit = 1)
                    success = success.message_on_delete_all_products
                    delete = True
        return {"success" : success, "delete" : delete}

#####################################################################################
## Delete the all products from Quick Order List baesd on product id accepted as json
#####################################################################################
    @route(['/quickorder/deleteallproduct'], type = "json", auth = "user", website = True)
    def delete_all_product(self, **kw):
        user_exists = request.env['quick.order'].search([('user_id', '=', request._uid),('state','=', 'draft')])
        if user_exists.quick_order_line:
            ids = [(2, id) for id in user_exists.quick_order_line.ids]
            user_exists.write({'quick_order_line':ids})
        success  = request.env['quick.order.message'].search([], limit = 1)
        return {"success" : success.message_on_delete_all_products}

################################################################################################
## Move Quick Order List into Order Cart as a single entity and change state of Quick Order List
################################################################################################
    @route(['/quickorder/createorder'], auth="user", type="json", website=True)
    def create_order(self,id=0, order_now=[], **kw):
        success  = request.env['quick.order.message'].search([], limit = 1)
        try :
            quick_order = request.env['quick.order'].browse(int(id))
        except Exception as e:
            raise Warning('Product id is invalid need int found String {}.'.format(e))
        if order_now and quick_order.state != 'done':
            total_lines = []
            sale_order = request.website.sale_get_order(force_create=1)
            if sale_order.order_line:
                total_lines = [order.product_id.id for order in sale_order.order_line]
            for order in order_now:
                if order.get('id') not in total_lines:
                        sale_order._cart_update(product_id = order['id'],line_id = None, set_qty = order.get('quantity'), add_qty = None)
                else:
                    order_line = request.env['sale.order.line'].sudo().search([('product_id', '=', order['id'])])
                    if len(order_line) > 0:
                        sale_order._cart_update(product_id = order.get('id'), line_id = order_line[0].id, add_qty = order.get('quantity'), set_qty = None )
            if not id:
                user_exists = request.env['quick.order'].search([('user_id', '=', request._uid),('state', '=', 'draft')])
            if id:
                user_exists = request.env['quick.order'].browse(id)
            user_exists.write({'state' : 'done'})
            return success.message_on_empty_order_list
        return {"error": success.empty_shopping_list_submit}

######################################################################################
## Move Quick Order List into Shopping List by changing the state of Quick Order List
######################################################################################
    @route(['/quickorder/addshoppinglist'], auth='user', type='json', website=True)
    def add_shopping_list(self, name='', id=None, create=False, list_id= 0, **kw):
        quick_order = request.env['quick.order'].browse(int(id))
        quick_order.write({"state": "done"})
        product_ids = []
        template = ''
        data = {}
        if id and create:
            if quick_order:
                quick_order.write({"name": name, "state": "shopping_list"})
                return {
                        "url" : "/quickorder/shoppinglist/"+str(quick_order.id),
                        "route" : True
                    }
        elif id and list_id:

            quick_order_1 = request.env['quick.order'].browse(int(list_id))
            products = self.shopping_list_availability(quick_order_1)
            for id in quick_order.quick_order_line:
                if id.product_id.id not in products:
                    product_ids.append((4,id.id))
                else:
                    q_products = quick_order_1.quick_order_line.filtered(lambda x: x.product_id.id == id.product_id.id)
                    if q_products.exists():
                        q_products.quantity = id.quantity + q_products.quantity
            if product_ids:
                quick_order_1.write({"quick_order_line": product_ids})
                quick_order.unlink()
            return {
                    "url" : "/quickorder/shoppinglist/"+str(quick_order_1.id),
                    "route" : True
                }
        return json.dumps({"route" : False})

##################################################################
## Get All Shopping List and also based on id
##################################################################
    @route(['/quickorder/shoppinglist', '/quickorder/shoppinglist/<int:shopping_id>'], auth='user', type='http', website=True)
    def shopping_list(self,shopping_id=0, id=0, **kw):
        shopping_lists = request.env['quick.order'].search([('user_id', '=', request._uid),('state', '=', 'shopping_list')])
        if id:
            shopping_list = request.env['quick.order'].search([('id', '=', int(id)),('state', '=', 'shopping_list'),('user_id', '=', request._uid)])
            return request.env['ir.ui.view'].render_template('quick_order.add_to_cart_mutliple',{
                                                                    'shopping_lists' : shopping_list,
                                                                    'shopping_list' : shopping_lists,
                                                                    'compute_currency' : self.compute_currency,
                                                                    'product_r': self.shopping_list_availability(shopping_list)
                                                                    })
        if shopping_id:
            shopping_list = request.env['quick.order'].search([('id', '=', shopping_id), ('state', '=', 'shopping_list'),('user_id', '=', request._uid)])
            try:
                len(shopping_list.quick_order_line)
            except Exception:
                shopping_list=None
        else:
            shopping_list = request.env['quick.order'].search([('user_id', '=', request._uid),('state', '=', 'shopping_list')])
        s_error = request.env['quick.order.message'].search([], limit = 1)
        return request.render('quick_order.shopping_list', {
                        'shopping_lists' : shopping_list,
                        'shopping_list' : shopping_lists,
                        'compute_currency' : self.compute_currency,
                        'error' :{'s_error': s_error.message_on_empty_shopping_list},
                        'product_r': self.shopping_list_availability(shopping_list)
                    })

####################################################################
## Delete all Shopping Lists and also baesd on unique id.
####################################################################
    @route(['/quickorder/shoppinglist/delete'], auth='user', type='http', website=True)
    def shopping_list_delete(self, shopping_id=0, product_id=0, **kw):
        if shopping_id:
            shopping_list = request.env['quick.order'].search([('id', '=', int(shopping_id)),('state', '=', 'shopping_list'), ('user_id', '=', request._uid)])
            if shopping_list:
                if int(product_id) in shopping_list.quick_order_line.ids:
                    shopping_list.write({"quick_order_line": [(2, int(product_id))]})
                elif not product_id:
                    shopping_list.unlink()
                    if len(request.env['quick.order'].search([('user_id', '=', request._uid),('state', '=', 'shopping_list')])) <= 0:
                        s_error = request.env['quick.order.message'].search([], limit = 1)
                        return request.env['ir.ui.view'].render_template('quick_order.404',{'error' :{'s_error': s_error.message_on_empty_shopping_list}})
                return json.dumps({'success' : "success"})
        return json.dumps({'error' : "error"})

############################################################################
## Move Shopping List into Order Cart and chnge the state of Shopping List.
############################################################################
    @route(['/quickorder/shoppinglist/curd'], auth='user', type='json', website=True)
    def shopping_list_curd(self, shopping_id, order_now = [] , **kw):
        quick_order = request.env['quick.order'].search([('id', '=', int(shopping_id)),('state', '=', 'shopping_list'), ('user_id', '=', request._uid)])
        if not order_now:
            order_now = [{'id': order.product_id.id, 'quantity': order.quantity} for order in quick_order.quick_order_line]
        if quick_order:
            return self.create_order(shopping_id,order_now)
        s_error = request.env['quick.order.message'].search([], limit = 1)
        return {"error": s_error.empty_shopping_list_submit}

    @route(['/my/quickorder'], auth='user', type='http', website=True)
    def my_quick_orders(self, **kw):
        total_quick_order = request.env['quick.order'].search([('user_id', '=', request._uid),('state', '=', 'done')])
        return request.render('quick_order.portal_my_quick_order',{'quick_orders':total_quick_order,'page_name':'quick_order'})

    @route(['/my/quickorder/<int:id>'], auth='user', type='http', website=True)
    def my_quick_orders_products(self, id=0, **kw):
        value = {}
        if id:
            total_quick_order = request.env['quick.order'].browse(id)
            value = {
                "name": total_quick_order.name,
                "quick_order": total_quick_order.quick_order_line,
                "compute_currency": self.compute_currency,
                "page_name": "quick_products"
                }
        return request.render('quick_order.portal_my_quick_order_details',value)

    @route(['/my/quickorder/update'], auth='user', type='http', website=True)
    def quick_order_recover_shopping_lists(self, id=0, action='', **kw):
        urls = '/quickorder'
        if id:
            try:
                id = int(id)
            except Exception:
                return request.redirect(urls)
            total_quick_order = request.env['quick.order'].browse(id)
            if action == 're-order':
                sale_order = request.website.sale_get_order(force_create=1)
                for products in total_quick_order.quick_order_line:
                    sale_order._cart_update(product_id = products.product_id.id,line_id = None,add_qty = products.quantity)
                urls = '/shop/cart'
            elif action == 'shopping-list' :
                total_quick_order.write({'state': 'shopping_list'})
                urls = '/quickorder/shoppinglist/'+str(total_quick_order.id)
        return request.redirect(urls)

    @route(['/quickorder/update/name'], auth="public", website=True, type="json")
    def update_shopping_list_name(self, s_name='', id=0, **kw):
        success = "No"
        name = ""
        if id:
            try:
                quick_order = request.env['quick.order'].browse(int(id))
                quick_order.write({'name':s_name})
                success = "ok"
                name = quick_order.name+str('<span class="open-e-sp-name"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></span>')
            except Exception:
                return {"success": "No"}
        return {"success": success, "name": name}

    @route(['/quickorder/shoppinglist/update/quantity'], auth="user", website="true", type="http")
    def update_quanity(self, line_id=0, qty=0, **kw):
        if line_id:
            quick_order = request.env['quick.order.line'].browse(int(line_id))
            quick_order.write({"quantity" : int(qty)})
            res = quick_order.product_id.product_tmpl_id._get_combination_info(product_id=quick_order.product_id.id, add_qty=quick_order.quantity)
        return json.dumps({"price" : res['price']})


class CustomerPortal(CustomerPortal):

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        values = super(CustomerPortal, self).home(**kw)
        total_quick_order = len(request.env['quick.order'].search([('user_id', '=', request._uid),('state', '=', 'done')]).ids)
        values.qcontext.update({"total_quick_order":total_quick_order})
        return values
