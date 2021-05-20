# -*- coding: utf-8 -*-
from odoo import http, fields
import ast

from odoo.http import request
from math import ceil
import requests
import json

import base64

import re
from datetime import datetime, timedelta
import pytz
import difflib

from exponent_server_sdk import DeviceNotRegisteredError
from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage
from exponent_server_sdk import PushResponseError
from exponent_server_sdk import PushServerError
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
import re
import math
from geopy.distance import geodesic
import numpy

class Main(http.Controller):

    @http.route('/getmenuapppos', type='json', auth='public', csrf=False)
    def get_products_app_pos(self, url, lang):

        payload = {"jsonrpc": "2.0", "params": {"lang": lang}}
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url + 'getmenuapp', headers=headers, data=json.dumps(payload))

        return response.json()['result']

    @http.route('/get_product_image_pos', type='json', auth='public', csrf=False)
    def get_product_image_pos(self, url, p_id, lang):

        payload = {"jsonrpc": "2.0", "params": {"p_id": p_id, "lang": lang}}
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url + 'get_product_image', headers=headers, data=json.dumps(payload))

        return response.json()['result']

    @http.route('/img_category', type='http', auth='public')
    def img_category(self, **kw):

        if kw.get('id'):
            product = request.env['product.public.category'].sudo().search([('id', '=', int(kw.get('id')))])

            content = base64.b64decode(str(product.image_512.decode("utf-8")))
            headers = {}
            headers['Access-Control-Allow-Origin'] = '*'
            headers = http.set_safe_image_headers(headers, content)
            response = request.make_response(content, headers)
            response.status_code = 200

            return response

    @http.route('/get_top_offers', type='json', auth='public', csrf=False)
    def get_top_offers(self, lang):

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        products = request.env['product.product'].sudo().with_context(lang=lang).search(
            [('status', '=', 'approved'), ('active', '=', True), ('type', '=', 'service'), ('is_offer', '=', True)])

        res = []

        for product in products:
            res.append({

                'id': product.id,
                'name': product.name,
                'price': product.lst_price,
                'salon': {'salon_id': product.marketplace_seller_id.id,
                          'salon_name': product.marketplace_seller_id.name},
                #       'image':'data:image/png;base64,'+str(product.image_128.decode("utf-8")) if product.image_128 else False,
                'image': base_url + '/img_product/?id=' + str(product.id) if product.image_1920 else False,
                'description': product.description_sale,
                'currency': product.currency_id.name,
                'discount_percentage': product.discount_percentage,
                'sales_count': product.sales_count,
                'service_time': product.service_time,
                'specialist': [{

                    "id": employee.id,
                    "image": base_url + '/salon_employee_img/?id=' + str(employee.id) if employee.image_1920 else False,
                    "name": employee.name,

                } for employee in product.related_specialist],

                'service_products': [{
                    "id": offer.id,
                    "name": offer.name,
                    "price": offer.lst_price,
                    'image': base_url + '/img_product/?id=' + str(offer.id) if offer.image_1920 else False,

                    'currency': offer.currency_id.name,

                } for offer in product.offer_products]

            })

        res = sorted(res, key=lambda r: r['sales_count'], reverse=True)
        return res

    @http.route('/get_salon_offers', type='json', auth='public', csrf=False)
    def get_salon_offers(self, r_id, lang):

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        products = request.env['product.product'].sudo().with_context(lang=lang).search(
            [('status', '=', 'approved'), ('marketplace_seller_id', '=', r_id), ('active', '=', True),
             ('type', '=', 'service'), ('is_offer', '=', True)])

        res = []

        for product in products:
            res.append({

                'id': product.id,
                'name': product.name,
                'price': product.lst_price,
                #       'image':'data:image/png;base64,'+str(product.image_128.decode("utf-8")) if product.image_128 else False,
                'image': base_url + '/img_product/?id=' + str(product.id) if product.image_1920 else False,
                'description': product.description_sale,
                'discount_percentage': product.discount_percentage,
                'currency': product.currency_id.name,
                'service_time': product.service_time,
                'specialist': [{

                    "id": employee.id,
                    "image": base_url + '/salon_employee_img/?id=' + str(employee.id) if employee.image_1920 else False,
                    "name": employee.name,

                } for employee in product.related_specialist],

                'service_products': [{
                    "id": offer.id,
                    "name": offer.name,
                    "price": offer.lst_price,
                    'image': base_url + '/img_product/?id=' + str(offer.id) if offer.image_1920 else False,

                    'currency': offer.currency_id.name,

                } for offer in product.offer_products]

            })

        return res

    @http.route('/get_salon_services', type='json', auth='public', csrf=False)
    def get_salon_services(self, r_id, lang):

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        products = request.env['product.product'].sudo().with_context(lang=lang).search(
            [('status', '=', 'approved'), ('marketplace_seller_id', '=', r_id), ('active', '=', True),
             ('type', '=', 'service'), ('is_offer', '=', False)])

        categories = request.env['product.public.category'].sudo().with_context(lang=lang).search([])

        application_data = []
        # routes=[]

        for category in categories:
            main_temp = []
            for product in products:
                if category.id in [cat.id for cat in product.public_categ_ids]:
                    temp = {
                        #         'total':product.list_price,
                        'id': product.id,
                        'name': product.name,
                        'price': product.lst_price,
                        #       'image':'data:image/png;base64,'+str(product.image_128.decode("utf-8")) if product.image_128 else False,
                        'image': base_url + '/img_product/?id=' + str(product.id) if product.image_1920 else False,
                        'description': product.description_sale,
                        'currency': product.currency_id.name,
                        'service_time': product.service_time,
                        'specialist': [{

                            "id": employee.id,
                            "image": base_url + '/salon_employee_img/?id=' + str(
                                employee.id) if employee.image_1920 else False,
                            "name": employee.name,

                        } for employee in product.related_specialist]
                        #     'pos_categ_id':product.categ_id.id,
                        #   'product_variant_count':product.product_variant_count,
                        #   'product_variant_ids':[[x.id,[[y.attribute_id.name,y.name,y.price_extra,False] for y in x.product_template_attribute_value_ids]] for x in product.product_variant_ids],
                        #  'addons':[[x.id,x.name,x.list_price,False] for x in product.addons],
                        #   'qty':1,
                        #  'pos_categ_name':product.categ_id.name,
                    }
                    main_temp.append(temp)

            if (main_temp.__len__() > 0):
                application_data.append({
                    'category_id': category.id,
                    'title': category.name,
                    'category_image': base_url + '/img_category/?id=' + str(
                        category.id) if category.image_1920 else False,
                    'services': main_temp})
                # routes.append({'key':category.id,'title':category.display_name})

        return {'application_data': application_data}

    @http.route('/get_product_image', type='json', auth='public')
    def image(self, p_id, lang):

        product = request.env['product.template'].sudo().with_context(lang=lang).search([('id', '=', p_id)])
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        temp = {

            'id': product.id,
            'name': product.display_name,
            'price': product.list_price,
            'total': product.list_price,
            'image': base_url + '/img_product/?id=' + str(product.id) if product.image_1920 else False,

            # 'image':base_url+'/web/image?model=product.template&id='+str(product.id)+'&field=image_1920',
            'description': product.description,
            'currency': product.currency_id.name,
            #     'pos_categ_id':product.categ_id.id,
            'product_variant_count': product.product_variant_count,
            'product_variant_ids': [[x.id, [[y.attribute_id.name, y.name, y.price_extra, False] for y in
                                            x.product_template_attribute_value_ids]] for x in
                                    product.product_variant_ids],
            'addons': [[x.id, x.name, x.list_price, False] for x in product.addons],
            'qty': 1,
            #  'pos_categ_name':product.categ_id.name,

        }

        return {
            'product': temp,
        }

    @http.route('/img_product', type='http', auth='public')
    def img(self, **kw):

        if kw.get('id'):
            product = request.env['product.template'].sudo().search([('id', '=', int(kw.get('id')))])

            content = base64.b64decode(str(product.image_512.decode("utf-8")))

            headers = {}
            headers['Access-Control-Allow-Origin'] = '*'
            headers = http.set_safe_image_headers(headers, content)
            response = request.make_response(content, headers)
            response.status_code = 200

            return response

    @http.route('/img_restaurant', type='http', auth='public')
    def img_restaurant(self, **kw):

        if kw.get('id'):
            product = request.env['res.partner'].sudo().search([('id', '=', int(kw.get('id')))])

            content = base64.b64decode(str(product.image_512.decode("utf-8")))
            headers = {}
            headers['Access-Control-Allow-Origin'] = '*'
            headers = http.set_safe_image_headers(headers, content)
            response = request.make_response(content, headers)
            response.status_code = 200

            return response

    @http.route('/salon_employee_img', type='http', auth='public')
    def salon_employee_img(self, **kw):

        if kw.get('id'):
            product = request.env['salon.employee'].sudo().search([('id', '=', int(kw.get('id')))])

            content = base64.b64decode(str(product.image_1920.decode("utf-8")))
            headers = {}
            headers['Access-Control-Allow-Origin'] = '*'
            headers = http.set_safe_image_headers(headers, content)
            response = request.make_response(content, headers)
            response.status_code = 200

            return response

    @http.route('/salon_gallery', type='http', auth='public')
    def salon_galley(self, **kw):

        if kw.get('id'):
            product = request.env['salon.gallery'].sudo().search([('id', '=', int(kw.get('id')))])

            content = base64.b64decode(str(product.image.decode("utf-8")))
            headers = {}
            headers['Access-Control-Allow-Origin'] = '*'
            headers = http.set_safe_image_headers(headers, content)
            response = request.make_response(content, headers)
            response.status_code = 200

            return response

    @http.route(['/qrscan'], type='http', methods=['GET'], auth="public", website=True)
    def get_qr_data(self, **kw):

        # myapp:///path/into/app?hello=world&goodbye=now

        return """
             <h1><a href="intent:///QrScreenCamera#Intent;scheme=waiteroo;package=com.waiteroo.order;end"> Take a QR code </a></h1>
         <script>
          if(navigator.userAgent.toLowerCase().indexOf("android") > -1){
                setTimeout(function(){
               window.location.href ='https://play.app.goo.gl/?link=https://play.google.com/store/apps/details?id=com.waiteroo.order&ddl=1&pcampaignid=web_ddl_1';
             },1000)
 }
 else if(navigator.userAgent.toLowerCase().indexOf("iphone") > -1 || navigator.userAgent.toLowerCase().indexOf("ipad") > -1 ){
                 window.location.href='waiteroo:///QrScreenCamera';
                setTimeout(function(){
                    window.location.href ='https://apps.apple.com/ae/app/waiteroo/id1514478193';
                },1000)
 }
         </script>
         <h1 style="text-align:center;margin-top: 250px">Only Scan QR using Waiteroo Application</h1><h1 style="text-align:center;margin-top: 50px">Website version coming soon</h1>"""

    # return {'r_id':kw.get('r_id'),'target':kw.get('target')}

    @http.route('/seller_api/login', type='json', auth='public', csrf=True)
    def salon_login(self, email, password):

        try:
            uid = request.session.authenticate(request.session.db, email, password)

            if uid:

                user = request.env['res.users'].sudo().search([('id', '=', uid)])

                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

                return {"user_id": uid,
                        "seller_id": user.partner_id.id,
                        'logo': base_url + '/img_restaurant/?id=' + str(
                            user.partner_id.id) if user.partner_id.image_1920 else False,
                        'seller_name': user.partner_id.name,
                        'is_seller': user.partner_id.seller,
                        'success': True,
                        'msg': 'Authenticated Successfully'
                        }
            else:
                return {
                    'success': False,
                    'msg': 'Invalid Username or Password'
                }
        except:
            return {
                'success': False,
                'msg': 'Invalid Username or Password'
            }

    @http.route(['/get_availabe_specialist'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def get_availabe_specialist(self, salon_id, date, service_id, start, end):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        previous_bookings = request.env['sale.order'].sudo().search(
            [('appointment_date', '=', date), ('related_seller.id', '=', salon_id)])

        if len(previous_bookings) == 0:

            service = request.env['product.product'].sudo().search([('id', '=', service_id)])
            specialist = list(map(lambda x: {
                "id": x.id,
                "image": base_url + '/salon_employee_img/?id=' + str(x.id) if x.image_1920 else False,
                "name": x.name,
            }, service.related_specialist))

            return specialist

        else:

            same_slot_order = list(filter(
                lambda x: (x.booking_start_time <= float(start.replace(":", ".")) <= x.booking_end_time) or (
                        x.booking_start_time <= float(end.replace(":", ".")) <= x.booking_end_time),
                previous_bookings))

            if len(same_slot_order) == 0:
                service = request.env['product.product'].sudo().search([('id', '=', service_id)])
                specialist = list(map(lambda x: {
                    "id": x.id,
                    "image": base_url + '/salon_employee_img/?id=' + str(x.id) if x.image_1920 else False,
                    "name": x.name,
                }, service.related_specialist))

                return specialist
            else:
                service = request.env['product.product'].sudo().search([('id', '=', service_id)])
                specialist = list(map(lambda x: {
                    "id": x.id,
                    "image": base_url + '/salon_employee_img/?id=' + str(x.id) if x.image_1920 else False,
                    "name": x.name,
                }, service.related_specialist))

                availabe_specailist = list(filter(lambda x: x['id'] not in list(
                    map(lambda y: y.id, same_slot_order[0].order_line.related_specialist)), specialist))

                return availabe_specailist

    @http.route(['/send_otp'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def send_otp(self, mobile, seq, appname):

        msg = "Your One-Time-Password (OTP) is " + str(
            seq) + ". Never share this OTP with anyone. Thank you for using " + appname + "."

        url = "https://mshastra.com/sendurlcomma.aspx?user=20084552&pwd=PANdora@321&senderid=PANDORA OTP&mobileno=" + mobile + "&msgtext=" + msg + "&priority=High&CountryCode=ALL"

        payload = {}
        headers = {

        }

        requests.request("GET", url, headers=headers, data=payload)

    @http.route(['/get_bookings'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def get_bookings(self, salon_id, date, service_time):
        service_time = service_time + 20
        today_date = fields.Date.today()
        today = False
        tz = pytz.timezone(request.env.user.tz) or pytz.utc
        day = pytz.utc.localize(datetime.today()).astimezone(tz).strftime('%A')
        hour = datetime.now(tz).hour + 1
        minute = 0
        current_time = str(hour) + '.' + str(minute)
        
        if today_date == datetime.strptime(date, '%Y-%m-%d').date():
            today = True

        salon = request.env['res.partner'].sudo().search([('id', '=', salon_id)])

        previous_bookings = request.env['sale.order'].sudo().search(
            [('appointment_date', '=', date), ('related_seller.id', '=', salon_id)])

        if len(previous_bookings) == 0:

            if today:
                start_time = current_time
            else:
                start_time = '0.0'
                # start_time = 0

            # end_time = 0
            end_time = '0.0'
            for slots in salon.timeslots:
                if slots.name.lower() == day.lower():

                    if not today:
                        start_time = slots.opening_time
                    end_time = slots.closing_time

                    break

            booking_slots = []

            from_date = datetime.strptime(date + " " + str(start_time), '%Y-%m-%d %H.%M')

            end_date = datetime.strptime(date + " " + str(end_time), '%Y-%m-%d %H.%M')

            while from_date < end_date:
                booking_slots.append({
                    'start': from_date.strftime('%Y-%m-%d %H:%M'),
                    'end': (from_date + timedelta(minutes=service_time)).strftime('%Y-%m-%d %H:%M')
                })

                from_date = from_date + timedelta(minutes=service_time)

            return booking_slots

        else:

            if today:
                start_time = current_time
            else:
                start_time = '0.0'
                # start_time = 0

            # end_time = 0
            end_time = '0.0'
            for slots in salon.timeslots:
                if slots.name.lower() == day.lower():

                    if not today:
                        start_time = slots.opening_time
                    end_time = slots.closing_time

                    break

            booking_slots = []

            from_date = datetime.strptime(date + " " + str(start_time), '%Y-%m-%d %H.%M')

            end_date = datetime.strptime(date + " " + str(end_time), '%Y-%m-%d %H.%M')

            previous_booking_time = [
                {'start': format(x.booking_start_time, ".2f"), 'end': format(x.booking_end_time, ".2f"),
                 'order_id': x.id} for x in previous_bookings]

            while from_date < end_date:

                found = list(filter(lambda x: (x['start'] <= from_date.strftime('%H.%M') <= x['end']) or (
                        x['start'] <= (from_date + timedelta(minutes=service_time)).strftime('%H.%M') <= x['end']),
                                    previous_booking_time))
                # found2=list(filter(lambda x: x['start'] <= (from_date+timedelta(minutes=service_time)).strftime('%H.%M')  <= x['end'], previous_booking_time))

                # found=found1+found2

                if len(found) > 0:

                    for value in found:

                        order = request.env['sale.order'].sudo().search([('id', '=', value['order_id'])])

                        order_specialist = list(filter(lambda x: x.related_specialist, order.order_line))

                        specialist = list(map(lambda x: {'id': x.related_specialist.id,
                                                         'department': x.related_specialist.department_id.id},
                                              order_specialist))

                        other_employees = request.env['salon.employee'].sudo().search(
                            [('department_id', '=', specialist[0]['department']), ('salon_id', '=', salon_id),
                             ('id', '!=', specialist[0]['id'])])

                        is_mapped = list(
                            filter(lambda x: x.id in [y.id for y in other_employees], salon.salon_employees))

                        if len(is_mapped) > 0:
                            booking_slots.append({
                                'start': from_date.strftime('%Y-%m-%d %H:%M'),
                                'end': (from_date + timedelta(minutes=service_time)).strftime('%Y-%m-%d %H:%M')
                            })

                    # print("Here-- already listed",from_date.strftime('%H.%M'))

                else:

                    booking_slots.append({
                        'start': from_date.strftime('%Y-%m-%d %H:%M'),
                        'end': (from_date + timedelta(minutes=service_time)).strftime('%Y-%m-%d %H:%M')
                    })

                from_date = from_date + timedelta(minutes=service_time)

            return booking_slots

    @http.route(['/submitorderapp'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def submit_order_waiteroo_app(self, cart_data, r_id, c_id):

        temp_order = {

            'partner_id': c_id,
            'partner_invoice_id': c_id,
            'partner_shipping_id': c_id,
            'related_seller': r_id,
            'pos_order_json': json.dumps(cart_data),
            'user_location_url': "https://www.google.com/maps/search/?api=1&query=" + str(
                cart_data.get('delivery_location')['latitude']) + "," + str(
                cart_data.get('delivery_location')['longitude']),
            'service_type': cart_data.get('service_type'),
            'appointment_date': cart_data.get('appointment_date'),
            'booking_start_time': cart_data.get('booking_start_time'),
            'booking_end_time': cart_data.get('booking_end_time')
        }

        waiteroo_order = request.env['sale.order'].sudo().create(temp_order)

        linesdata = []

        for line in cart_data.get('lines'):
            linesdata.append(

                {'product_id': line.get('product_id'), 'product_uom_qty': line.get('qty'),
                 'price_unit': line.get('price_unit'), 'name': line.get('product_note') or '',
                 'related_specialist': line.get('related_specialist'), 'order_id': waiteroo_order.id}
            )

            # for addon in line.get('addons'):

            #     linesdata.append(

            #     {'product_id':addon.get('id'),'product_uom_qty':addon.get('qty'),'price_unit':addon.get('price'),'name':'+ Addons','order_id':waiteroo_order.id}
            # )

        if (cart_data.get('delivery_charge') > 0):
            delivery_product = request.env['product.product'].sudo().search(
                [('name', '=', 'Free delivery charges'), ('active', '=', True)], limit=1)

            if delivery_product:
                linesdata.append(

                    {'product_id': delivery_product.id, 'product_uom_qty': 1,
                     'price_unit': cart_data.get('delivery_charge'), 'name': 'Delivery Product',
                     'order_id': waiteroo_order.id}
                )

        request.env['sale.order.line'].sudo().create(linesdata)

        try:

            self.send_push_message(waiteroo_order.related_seller.client_notification_token, waiteroo_order.name,
                                   'New Order recieved from ' + waiteroo_order.partner_id.name + '\n',
                                   {'n_type': 'order_tracking', 'order_id': waiteroo.id})

        except:

            pass

        return {'id': waiteroo_order.id, 'name': waiteroo_order.name}

    @http.route(['/checkcustomer'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def check_customer(self, phone):

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        previous_customer = request.env['res.partner'].sudo().search(
            [('phone', '=', phone), ('waiteroo_customer', '=', True)])

        if previous_customer:
            return {'id': previous_customer.id, 'email': previous_customer.email, 'name': previous_customer.name,
                    'gender': previous_customer.gender, 'addresses': previous_customer.addresses,
                    'favourite_salons': previous_customer.favourite_restaurants, 'phone': previous_customer.phone,
                    'image': base_url + '/img_restaurant/?id=' + str(previous_customer.id) if previous_customer.image_1920 else False}

    @http.route(['/createcustomer'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def create_customer(self, phone, name, gender, email, push_token, addresses, favourite_salons):

        previous_customer = request.env['res.partner'].sudo().search([('phone', '=', phone)])

        if previous_customer:
            previous_customer.sudo().write({

                'name': name,
                'gender': gender,
                'email': email,
                'customer_notification_token': push_token,
                'addresses': addresses,
                'favourite_restaurants': favourite_salons
            })

            return {'id': previous_customer.id}

        if not previous_customer:
            temp = {

                'name': name,
                'mobile': phone,
                'phone': phone,
                'email': email,
                'waiteroo_customer': True,
                'gender': gender,
                'customer_notification_token': push_token,
                'addresses': addresses,
                'favourite_restaurants': favourite_salons

            }

            waiteroo_customer = request.env['res.partner'].sudo().create(temp)

            return {'id': waiteroo_customer.id}

    @http.route(['/changestate'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def changestate(self, order_name, state):

        reason = ''

        waiteroo = request.env['sale.order'].sudo().search([('name', '=', order_name)])

        if waiteroo.client_order_ref:

            if state == 'accepted':

                if waiteroo.state == 'rejected':
                    waiteroo.sudo().write({'state': 'cancel'})
                    waiteroo.sudo().action_draft()
                    waiteroo.sudo().action_confirm()
                    waiteroo.sudo().write({'state': state})
                else:

                    waiteroo.sudo().action_confirm()
                    waiteroo.sudo().write({'state': state})


            else:
                if (state == 'cancel' or state == 'rejected'):
                    waiteroo.sudo().action_cancel()
                    waiteroo.sudo().write({'state': 'rejected'})
                else:
                    # waiteroo.sudo().action_cancel()
                    waiteroo.sudo().write({'state': state})

            # send push notification here to customer

            if waiteroo.partner_id.customer_notification_token and waiteroo.partner_id.customer_notification_token != "tocke":
                # send push notification here to customer
                if reason:
                    reason = '(' + reason + ')'
                self.send_push_message(waiteroo.partner_id.customer_notification_token,
                                       waiteroo.client_order_ref if waiteroo.client_order_ref else waiteroo.name,
                                       'Your order is ' + state + '\n' + reason,
                                       {'n_type': 'order_tracking', 'order_id': waiteroo.id})

            return state

    @http.route(['/changestate_non_pos', '/api/changestate_non_pos'], type='json', auth="public", methods=['POST'],
                website=True, csrf=False)
    def changestate_non_pos(self, order_name, state, reason=False):

        waiteroo = request.env['sale.order'].sudo().search([('id', '=', order_name)])

        waiteroo.sudo().write({
            'r_comments': reason,
            'state': state
        })

        try:

            self.send_push_message(waiteroo.partner_id.customer_notification_token,
                                   waiteroo.client_order_ref if waiteroo.client_order_ref else waiteroo.name,
                                   'Your order is ' + state + '\n',
                                   {'n_type': 'order_tracking', 'order_id': waiteroo.id})

        except:

            pass

        return state

    @http.route(['/res_action'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def res_action(self, is_busy, website):

        restaurant = request.env['res.partner'].sudo().search([('website', '=', website + '/')], limit=1)

        restaurant.sudo().write({'is_busy': is_busy})

        return True

    @http.route(['/res_action_get'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def res_action_get(self, website):

        restaurant = request.env['res.partner'].sudo().search([('website', '=', website + '/')], limit=1)

        return {'is_busy': restaurant.is_busy}

    @http.route(['/update_customer_addres_odoo'], type='json', auth="public", methods=['POST'], website=True,
                csrf=False)
    def update_customer_addres_odoo(self, c_id, addresses):

        customer = request.env['res.partner'].sudo().search([('id', '=', c_id)])

        if customer:
            customer.sudo().write({'addresses': addresses});

    @http.route(['/update_customer_info'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def update_customer_info(self, c_id, name, email, gender):

        customer = request.env['res.partner'].sudo().search([('id', '=', c_id)])

        if customer:
            customer.sudo().write({
                'name': name,
                'email': email,
                'gender': gender
            })

    @http.route(['/update_customer_image'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def update_customer_image(self, c_id, image):

        customer = request.env['res.partner'].sudo().search([('id', '=', c_id)])

        if customer:
            customer.sudo().write({
                'image_1920': image
            })

    @http.route(['/update_customer_token'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def update_customer_token(self, c_id, push_token):

        customer = request.env['res.partner'].sudo().search([('id', '=', c_id)])

        if customer:
            customer.sudo().write({'customer_notification_token': push_token})

    @http.route(['/update_salon_token'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def update_salon_token(self, r_id, push_token):

        salon = request.env['res.partner'].sudo().search([('id', '=', r_id)])

        if salon:
            salon.sudo().write({'client_notification_token': push_token})

    @http.route(['/update_push_token_public'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def update_push_token_public(self, push_token):

        old = request.env['waiteroo.public.notification'].sudo().search([('name', '=', push_token)], limit=1)

        if not old:
            request.env['waiteroo.public.notification'].sudo().create({
                'name': push_token
            })

    @http.route(['/getallorderres', '/api/getallorderres'], type='json', auth="public", methods=['POST'], website=True,
                csrf=False)
    def getallorderres(self, r_id, last_id):

        if last_id:

            new_order = request.env['res.partner'].sudo().search([('id', '=', r_id)], limit=1)

            if new_order.id == last_id:
                return

        restaurant = request.env['res.partner'].sudo().search([('id', '=', r_id)], limit=100)

        if restaurant:

            # customize it later for Multiple Countries

            tz = pytz.timezone(request.env.user.tz) or pytz.utc

            orders = request.env['sale.order'].sudo().search([('related_seller', '=', restaurant.id)])

            res = []
            # base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            for order in orders:
                res.append({
                    'id': order.id,
                    'name': order.client_order_ref if order.client_order_ref else order.name,
                    'state': order.state,
                    'selected_table': json.loads(order.pos_order_json)['selected_table'],
                    #  'order_json':order.pos_order_json,
                    #  'pos_order':order.pos_order,
                    #    'related_seller':[[x.name,x.id,'data:image/png;base64,'+str(x.image_1920.decode("utf-8")) if x.image_1920 else base_url+'/waiteroo_market_place_portal_configuration/static/description/icon.png',x.res_location,x.phone] for x in order.related_seller],
                    #  'client_order_ref':order.client_order_ref,
                    'amount_total': order.amount_total,
                    #  'amount_untaxed':order.amount_untaxed,
                    #  'amount_tax':order.amount_tax,
                    'date_order': pytz.utc.localize(order.date_order).astimezone(tz).strftime("%d/%m/%Y, %I:%M %p"),
                    'currency': order.currency_id.name,

                })

            return res

    @http.route(['/get_all_orders_ongoing_dates'], type='json', auth="public", methods=['POST'], website=True,
                csrf=False)
    def get_all_orders_ongoing_dates(self, c_id):

        customer = request.env['res.partner'].sudo().search([('id', '=', c_id)])

        if customer:
            # customize it later for Multiple Countries

            tz = pytz.timezone(request.env.user.tz) or pytz.utc

            orders = request.env['sale.order'].sudo().search(
                [('partner_id', '=', customer.id), ('state', 'in', ['draft', 'accepted']),
                 ('appointment_date', '>=', fields.Date.today())], order='appointment_date desc')

            return list(map(lambda x: x.appointment_date, orders))

    @http.route(['/get_all_orders_ongoing'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def get_all_orders_ongoing(self, c_id, date):

        customer = request.env['res.partner'].sudo().search([('id', '=', c_id)])

        if customer:

            # customize it later for Multiple Countries

            tz = pytz.timezone(request.env.user.tz) or pytz.utc

            # ('state','in',['completed','rejected'])

            orders = request.env['sale.order'].sudo().search(
                [('partner_id', '=', customer.id), ('state', 'in', ['draft', 'accepted']),
                 ('appointment_date', '=', date)], order='appointment_date desc')

            res = []
            # base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            for order in orders:
                res.append({
                    'id': order.id,
                    'name': order.client_order_ref if order.client_order_ref else order.name,
                    'state': order.state,
                    'booking_start_time': format(order.booking_start_time, ".2f"),
                    'booking_end_time': format(order.booking_end_time, ".2f"),
                    'service_type': order.service_type,
                    'user_location_url': order.user_location_url,
                    'Salon_location': "https://www.google.com/maps/search/?api=1&query="+order.related_seller.res_location,
                    #  'order_json':order.pos_order_json,
                    #  'pos_order':order.pos_order,
                    'related_seller': [
                        [x.name, x.street + ' ' + x.city + ' ' + x.state_id.name + ' ' + x.country_id.name,
                         'data:image/png;base64,' + str(x.image_128.decode("utf-8")) if x.image_128 else False] for x in
                        order.related_seller],
                    #  'client_order_ref':order.client_order_ref,
                    'amount_total': order.amount_total,
                    #  'amount_untaxed':order.amount_untaxed,
                    #  'amount_tax':order.amount_tax,
                    'appointment_date': order.appointment_date,
                    #      'appointment_date':pytz.utc.localize(order.appointment_date).astimezone(tz).strftime("%d/%m/%Y, %I:%M %p"),
                    'currency': order.currency_id.name,
                    'order_lines': [{
                        'namme': line.product_id.name,
                        'price': line.price_unit,
                        'specialist_name': line.related_specialist.name
                    } for line in order.order_line]

                })

            return res

    @http.route(['/post_review'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def post_review(self, r_id, c_id, title, message, rating):

        review = request.env['seller.review'].sudo().create({

            'title': title,
            'msg': message,
            'marketplace_seller_id': r_id,
            'partner_id': c_id,
            'rating': rating,

        })

        review.toggle_website_published()

        return {
            'msg': 'Review posted successfully'
        }

    @http.route(['/post_review_specialist'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def post_review_specialist(self, specialist_id, c_id, title, rating):

        # review=request.env['salon.employee.rating'].sudo().create({

        #     'title':title,
        #     'employee_id':specialist_id,
        #     'customer':c_id,
        #     'rating':rating

        # })

        employee = request.env['salon.employee'].sudo().search([('id', '=', specialist_id)])

        employee.sudo().write({
            'employee_ratings': [
                [
                    0,
                    0,
                    {
                        'title': title,
                        'employee_id': specialist_id,
                        'customer': c_id,
                        'rating': rating
                    }
                ]
            ]
        })

        return {
            'msg': 'Review posted successfully'
        }

    @http.route(['/get_all_orders_history'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def get_all_orders_history(self, c_id):

        customer = request.env['res.partner'].sudo().search([('id', '=', c_id)])

        if customer:

            # customize it later for Multiple Countries

            tz = pytz.timezone(request.env.user.tz) or pytz.utc

            # ('state','in',['completed','rejected'])

            orders = request.env['sale.order'].sudo().search(
                [('partner_id', '=', customer.id), ('state', 'in', ['completed', 'rejected'])],
                order='appointment_date desc')

            res = []
            # base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            for order in orders:
                res.append({
                    'id': order.id,
                    'name': order.client_order_ref if order.client_order_ref else order.name,
                    'state': order.state,
                    'service_type': order.service_type,
                    'user_location_url': order.user_location_url,
                    'Salon_location': "https://www.google.com/maps/search/?api=1&query="+order.related_seller.res_location,

                    #  'order_json':order.pos_order_json,
                    #  'pos_order':order.pos_order,
                    'related_seller': [
                        [x.name, x.street + ' ' + x.city + ' ' + x.state_id.name + ' ' + x.country_id.name,
                         'data:image/png;base64,' + str(x.image_128.decode("utf-8")) if x.image_128 else False] for x in
                        order.related_seller],
                    #  'client_order_ref':order.client_order_ref,
                    'amount_total': order.amount_total,
                    #  'amount_untaxed':order.amount_untaxed,
                    #  'amount_tax':order.amount_tax,
                    'appointment_date': order.appointment_date,
                    'booking_start_time': format(order.booking_start_time, ".2f"),
                    'booking_end_time': format(order.booking_end_time, ".2f"),
                    #      'appointment_date':pytz.utc.localize(order.appointment_date).astimezone(tz).strftime("%d/%m/%Y, %I:%M %p"),
                    'currency': order.currency_id.name,
                    'order_lines': [{
                        'namme': line.product_id.name,
                        'price': line.price_unit,
                        'specialist_name': line.related_specialist.name
                    } for line in order.order_line]

                })

            return res

    @http.route(['/get_all_orders_salons'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def get_all_orders_salons(self, r_id):

        customer = request.env['res.partner'].sudo().search([('id', '=', r_id)])

        if customer:

            # customize it later for Multiple Countries

            tz = pytz.timezone(request.env.user.tz) or pytz.utc

            # ('state','in',['completed','rejected'])

            orders = request.env['sale.order'].sudo().search([('related_seller', '=', customer.id)],
                                                             order='appointment_date desc')

            res = []
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            for order in orders:
                res.append({
                    'id': order.id,
                    'name': order.client_order_ref if order.client_order_ref else order.name,
                    'state': order.state,
                    'service_type': order.service_type,
                    'booking_start_time': format(order.booking_start_time, ".2f"),
                    'booking_end_time': format(order.booking_end_time, ".2f"),
                    'customer_location': order.user_location_url,
                    'customer': {'name': order.partner_id.name, 'phone': order.partner_id.phone,
                                 "customer_image": base_url + '/img_restaurant/?id=' + str(
                                     order.partner_id.id) if order.partner_id.image_1920 else False, },
                    #  'order_json':order.pos_order_json,
                    #  'pos_order':order.pos_order,
                    'related_seller': [
                        [x.name, x.street + ' ' + x.city + ' ' + x.state_id.name + ' ' + x.country_id.name,
                         'data:image/png;base64,' + str(x.image_128.decode("utf-8")) if x.image_128 else False] for x in
                        order.related_seller],
                    #  'client_order_ref':order.client_order_ref,
                    'amount_total': order.amount_total,
                    #  'amount_untaxed':order.amount_untaxed,
                    #  'amount_tax':order.amount_tax,
                    'appointment_date': order.appointment_date,
                    #      'appointment_date':pytz.utc.localize(order.appointment_date).astimezone(tz).strftime("%d/%m/%Y, %I:%M %p"),
                    'currency': order.currency_id.name,
                    'order_lines': [{
                        'namme': line.product_id.name,
                        'price': line.price_unit,
                        'specialist_name': line.related_specialist.name
                    } for line in order.order_line]

                })

            return res

    @http.route(['/vieworderd', '/api/vieworderd'], type='json', auth="public", methods=['POST'], website=True,
                csrf=False)
    def vieworderd(self, order_id):

        orders = request.env['sale.order'].sudo().search([('id', '=', order_id)])

        res = []

        tz = pytz.timezone(request.env.user.tz) or pytz.utc

        for order in orders:
            res.append({
                #   'id':order.id,
                'name': order.client_order_ref if order.client_order_ref else order.name,
                #    'state':order.state,
                'order_json': order.pos_order_json,
                'r_comments': order.r_comments,
                'state': order.state,
                #  'pos_order':order.pos_order,
                'profile_banner': 'data:image/png;base64,' + str(order.related_seller.profile_banner.decode(
                    "utf-8")) if order.related_seller.profile_banner else False,
                'related_seller': [[x.name, x.id, 'data:image/png;base64,' + str(
                    x.image_128.decode("utf-8")) if x.image_128 else False, x.res_location, x.phone] for x in
                                   order.related_seller],

                #  'client_order_ref':order.client_order_ref,
                #   'amount_total':order.amount_total,
                #  'amount_untaxed':order.amount_untaxed,
                #  'amount_tax':order.amount_tax,
                'date_order': pytz.utc.localize(order.date_order).astimezone(tz).strftime("%d/%m/%Y, %I:%M %p"),
                #   'currency':order.currency_id.name,

            })

        return res

    #     @http.route(['/vieworderdcustomer'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    #     def vieworderdcustomer(self,order_id):
    #
    #
    #
    #
    #
    #
    #
    #         orders=request.env['sale.order'].sudo().search([('id','=',order_id)])
    #
    #         res = []
    #
    #
    #
    #         for order in orders:
    #
    #             res.append({
    #              #   'id':order.id,
    #              #   'name':order.client_order_ref if order.client_order_ref else order.name ,
    #             #    'state':order.state,
    #                 'order_json':order.pos_order_json,
    #               #  'pos_order':order.pos_order,
    #              'profile_banner':'data:image/png;base64,'+str(order.related_seller.profile_banner.decode("utf-8")) if order.related_seller.profile_banner else False,
    #               #  'client_order_ref':order.client_order_ref,
    #              #   'amount_total':order.amount_total,
    #               #  'amount_untaxed':order.amount_untaxed,
    #               #  'amount_tax':order.amount_tax,
    #              #   'date_order':pytz.utc.localize(order.date_order).astimezone(tz).strftime("%d/%m/%Y, %I:%M %p"),
    #              #   'currency':order.currency_id.name,
    #
    #
    #             })
    #
    #
    #
    #
    #         return res

    @http.route('/checkdelivery', type='json', auth='public')
    def checkdelivery(self, r_id, area):

        restaurant = request.env['res.partner'].sudo().search([('id', '=', r_id)])
        all_ref = [x.name.lower() for x in restaurant.delivery_areas]

        to_check = area.lower().replace("'", '').split(" ")
        for word in to_check:

            found = difflib.get_close_matches(word, all_ref)
            if found:
                matched_area = found
                return True

        matched_area = difflib.get_close_matches(area.lower().replace("'", ''), all_ref)
        if len(matched_area) > 0:
            return True

        return False

    @http.route('/checkorderstatus', type='json', auth='public')
    def checkorderstatus(self, id):

        order = request.env['sale.order'].sudo().search(
            [('id', '=', id), ('state', 'not in', ['rejected', 'completed'])])

        if order:
            return True

        else:

            return False

    @http.route('/waiteroo_clients_delivery', type='json', auth='public')
    def get_waiteroo_clients_delivery(self, area, lang, city, country, lat, lng):
        res = []

        res_open = []
        res_close = []

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        tz = pytz.timezone(request.env.user.tz) or pytz.utc

        day = pytz.utc.localize(datetime.today()).astimezone(tz).strftime('%A')
        hour = datetime.now(tz).hour
        minute = datetime.now(tz).minute
        time = float(str(hour) + '.' + str(minute))

        source = (lat, lng)

        if area == 'All':

            matching = request.env['delivery.area'].sudo().search([], limit=100)

        else:

            # print("here--- area",area)

            matching = request.env['delivery.area'].sudo().search([])

            all_ref = [x.name.lower() for x in matching]
            to_check = area.lower().replace("'", '').split(" ")
            matched_area = []
            for word in to_check:

                found = difflib.get_close_matches(word, all_ref)
                if found:
                    matched_area = found
                    break

            if len(matched_area) > 0:
                matching = request.env['delivery.area'].sudo().with_context(lang=lang).search(
                    [('name', 'ilike', matched_area[0])])
            else:
                matched_area = difflib.get_close_matches(area.lower().replace("'", ''), all_ref)

                if len(matched_area) > 0:
                    matching = request.env['delivery.area'].sudo().with_context(lang=lang).search(
                        [('name', 'ilike', matched_area[0])])
                else:

                    request.env['waiteroo.area.log'].sudo().create({

                        name: area,
                        city: city,
                        country: country
                    })

                    demo_res = request.env['res.partner'].sudo().with_context(lang=lang).search([('id', '=', 7)])

                    for r in demo_res:
                        res_open.append({
                            'name': r.name,
                            'has_delivery': r.has_delivery,
                            'has_pickup': r.has_pickup,
                            'has_qrscan': r.has_qrscan,
                            'res_location': r.res_location,
                            'delivery_zone': r.delivery_zone,
                            'delivery_est': r.delivery_est,
                            'delivery_charges': r.delivery_charges,
                            'is_featured': r.is_featured,
                            'minimum_order': r.minimum_order,
                            'has_promotions': r.has_promotions,
                            # 'timeslots':timeslots,
                            'website': r.website,
                            'is_busy': r.is_busy,
                            'area': area,
                            # 'polygon':area.polygon,
                            'id': r.id,
                            'today': False,

                            'open': True,
                            #  'image_medium':'data:image/png;base64,'+r.image_medium if r.image_medium else r.website+'/waiteroo_website_customer/static/description/icon.png',
                            #   'image_small':'data:image/png;base64,'+r.image_small if r.image_small else r.website+'/waiteroo_website_customer/static/description/icon.png',
                            #      'image':'data:image/png;base64,'+str(r.image_128.decode("utf-8")) if r.image_128 else False,
                            'image': base_url + '/img_restaurant/?id=' + str(r.id) if r.image_1920 else False,
                            #      'profile_banner':'data:image/png;base64,'+str(r.profile_banner.decode("utf-8")) if r.profile_banner else False,

                            #  'image':base_url+'/web/image?model=res.partner&id='+str(r.id)+'&field=image_1920',
                            'tag_line': r.tag_line,
                            'currency': r.currency_id.name,
                            'has_tax': r.has_tax,
                            'tax_type': r.tax_type,
                            'tax_percentage': r.tax_percentage,
                            'cuisine': ', '.join([x.name for x in r.cuisine])

                        })

                    return res_open

        #             matching = request.env['delivery.area'].sudo().search([])
        #
        #
        #
        #
        #
        #             matching=[x for x in matching if (area in x.name or x.name in area)]

        # matched=

        # print("Here---",matching)

        for area in matching:

            for r in area.restaurant:

                open = True

                today = False

                distance = 0

                if r.has_delivery:

                    if r.res_location:
                        destination = r.res_location.split(",")
                        destination = (float(destination[0]), float(destination[1]))

                        distance = geodesic(source, destination).km

                    for slots in r.timeslots:
                        if slots.name.lower() == day.lower():
                            today = self.calculate_time(slots.opening_time) + ' - ' + self.calculate_time(
                                slots.closing_time)
                            if time < slots.opening_time or time > slots.closing_time:
                                open = False
                                break

                    #                     timeslots=[]
                    #                     for t in r.timeslots:
                    #                         timeslots.append({
                    #                             'name':t.name,
                    #                             'opening_time':t.opening_time,
                    #                             'closing_time':t.closing_time,
                    #                         })

                    if not open or r.is_busy:

                        res_close.append({

                            'name': r.name,
                            'has_delivery': r.has_delivery,
                            'has_pickup': r.has_pickup,
                            'has_qrscan': r.has_qrscan,
                            'res_location': r.res_location,
                            'delivery_zone': r.delivery_zone,
                            'delivery_est': (math.floor((distance / 60) * 60) + 3) + r.delivery_est,
                            'distance_sort': distance,
                            'delivery_charges': r.delivery_charges,
                            'is_featured': r.is_featured,
                            'minimum_order': r.minimum_order,
                            'has_promotions': r.has_promotions,
                            # 'timeslots':timeslots,
                            'website': r.website,
                            'today': today,
                            'is_busy': r.is_busy,
                            'area': area.name,
                            'polygon': area.polygon,
                            'id': r.id,

                            'open': open,
                            #  'image_medium':'data:image/png;base64,'+r.image_medium if r.image_medium else r.website+'/waiteroo_website_customer/static/description/icon.png',
                            #   'image_small':'data:image/png;base64,'+r.image_small if r.image_small else r.website+'/waiteroo_website_customer/static/description/icon.png',
                            #      'image':'data:image/png;base64,'+str(r.image_128.decode("utf-8")) if r.image_128 else False,
                            'image': base_url + '/img_restaurant/?id=' + str(r.id) if r.image_1920 else False,
                            #      'profile_banner':'data:image/png;base64,'+str(r.profile_banner.decode("utf-8")) if r.profile_banner else False,

                            #  'image':base_url+'/web/image?model=res.partner&id='+str(r.id)+'&field=image_1920',
                            'tag_line': r.tag_line,
                            'currency': r.currency_id.name,
                            'has_tax': r.has_tax,
                            'tax_type': r.tax_type,
                            'tax_percentage': r.tax_percentage,
                            'cuisine': ', '.join([x.name for x in r.cuisine])

                        })
                    else:

                        res_open.append({
                            'name': r.name,
                            'has_delivery': r.has_delivery,
                            'has_pickup': r.has_pickup,
                            'has_qrscan': r.has_qrscan,
                            'res_location': r.res_location,
                            'delivery_zone': r.delivery_zone,
                            'delivery_est': (math.floor((distance / 60) * 60) + 3) + r.delivery_est,
                            'distance_sort': distance,
                            'delivery_charges': r.delivery_charges,
                            'is_featured': r.is_featured,
                            'minimum_order': r.minimum_order,
                            'has_promotions': r.has_promotions,
                            # 'timeslots':timeslots,
                            'website': r.website,
                            'is_busy': r.is_busy,
                            'area': area.name,
                            'polygon': area.polygon,
                            'id': r.id,
                            'today': today,
                            'open': open,
                            #  'image_medium':'data:image/png;base64,'+r.image_medium if r.image_medium else r.website+'/waiteroo_website_customer/static/description/icon.png',
                            #   'image_small':'data:image/png;base64,'+r.image_small if r.image_small else r.website+'/waiteroo_website_customer/static/description/icon.png',
                            #      'image':'data:image/png;base64,'+str(r.image_128.decode("utf-8")) if r.image_128 else False,
                            'image': base_url + '/img_restaurant/?id=' + str(r.id) if r.image_1920 else False,
                            #      'profile_banner':'data:image/png;base64,'+str(r.profile_banner.decode("utf-8")) if r.profile_banner else False,

                            #  'image':base_url+'/web/image?model=res.partner&id='+str(r.id)+'&field=image_1920',
                            'tag_line': r.tag_line,
                            'currency': r.currency_id.name,
                            'has_tax': r.has_tax,
                            'tax_type': r.tax_type,
                            'tax_percentage': r.tax_percentage,
                            'cuisine': ', '.join([x.name for x in r.cuisine])

                        })

        #         if len(res_open)==0:
        #
        #             demo_res=request.env['res.partner'].sudo().with_context(lang=lang).search([('id','=',7)])
        #
        #             for r in demo_res:
        #                 res_open.append({
        #                             'name':r.name,
        #                             'has_delivery':r.has_delivery,
        #                             'has_pickup':r.has_pickup,
        #                             'has_qrscan':r.has_qrscan,
        #                             'res_location':r.res_location,
        #                             'delivery_zone':r.delivery_zone,
        #                             'delivery_est':r.delivery_est,
        #                             'delivery_charges':r.delivery_charges,
        #                             'is_featured':r.is_featured,
        #                             'minimum_order':r.minimum_order,
        #                             'has_promotions':r.has_promotions,
        #                             #'timeslots':timeslots,
        #                             'website':r.website,
        #                             'is_busy':r.is_busy,
        #                             'area':area.name,
        #                             'polygon':area.polygon,
        #                             'id':r.id,
        #
        #                              'open':True,
        #                           #  'image_medium':'data:image/png;base64,'+r.image_medium if r.image_medium else r.website+'/waiteroo_website_customer/static/description/icon.png',
        #                          #   'image_small':'data:image/png;base64,'+r.image_small if r.image_small else r.website+'/waiteroo_website_customer/static/description/icon.png',
        #                       #      'image':'data:image/png;base64,'+str(r.image_128.decode("utf-8")) if r.image_128 else False,
        #                             'image':base_url+'/img_restaurant/?id='+str(r.id) if r.image_1920 else False,
        #                      #      'profile_banner':'data:image/png;base64,'+str(r.profile_banner.decode("utf-8")) if r.profile_banner else False,
        #
        #                          #  'image':base_url+'/web/image?model=res.partner&id='+str(r.id)+'&field=image_1920',
        #                             'tag_line':r.tag_line,
        #                             'currency':r.currency_id.name,
        #                             'has_tax':r.has_tax,
        #                             'tax_type':r.tax_type,
        #                             'tax_percentage':r.tax_percentage,
        #                             'cuisine': ', '.join([x.name for x in r.cuisine])
        #
        #
        #                         })

        res = sorted(res_open, key=lambda r: r['distance_sort']) + sorted(res_close, key=lambda r: r['distance_sort'])
        return res

    def calculate_time(self, time):

        if (time >= 12):

            time = round(time - 12, 2)
            if time < 1:
                time = time + 12

            time = str(time).replace(".", ":")

            if len(time) < 5:
                time = str(time).replace(":0", ":00")
            return time + ' PM'

        else:
            time = str(time).replace(".", ":")

            if len(time) < 5:
                time = str(time).replace(":0", ":00")
            return time + ' AM'
    
    def get_today_time(self,timeslots):
        tz = pytz.timezone(request.env.user.tz) or pytz.utc

        day = pytz.utc.localize(datetime.today()).astimezone(tz).strftime('%A')
        hour = datetime.now(tz).hour
        minute = datetime.now(tz).minute
        time = float(str(hour) + '.' + str(minute))
        for slots in timeslots:
                    if slots.name.lower() == day.lower():
                        return self.calculate_time(slots.opening_time) + ' - ' + self.calculate_time(
                            slots.closing_time)

    def get_salon_status(self,timeslots):
        open=True
        tz = pytz.timezone(request.env.user.tz) or pytz.utc

        day = pytz.utc.localize(datetime.today()).astimezone(tz).strftime('%A')
        hour = datetime.now(tz).hour
        minute = datetime.now(tz).minute
        time = float(str(hour) + '.' + str(minute))
        for slots in timeslots:
                    if slots.name.lower() == day.lower():

                        if time < slots.opening_time or time > slots.closing_time:
                            open = False
                            break 
                            
        return open 
    
    @http.route('/salon_info',type='json',auth='public')
    def salon_info(self,salon_id):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        salon = list(map(lambda r:{

            'name': r.name,
                        'home_service': r.has_delivery,
                        'salon_service': r.has_pickup,
                        'has_qrscan': r.has_qrscan,
                        'salon_location': r.res_location,
                        'delivery_zone': r.delivery_zone,
                        #          'delivery_est':r.delivery_est,
                        'delivery_charges': r.delivery_charges,
                        'is_featured': r.is_featured,
                        'minimum_order': r.minimum_order,
                        'has_promotions': r.has_promotions,
                        # 'timeslots':timeslots,
                        'is_busy': r.is_busy,
                        'website': r.website,
                        'average_rating': r.average_rating,
                        'today': self.get_today_time(r.timeslots),
                        'id': r.id,
                        'open': self.get_salon_status(r.timeslots),
                        'salon_address': (r.street + ' ' if r.street else '') + (r.city + ' ' if r.city else '') + (
                            r.state_id.name + ' ' if r.state_id.name else '') + (
                                             r.country_id.name if r.country_id.name else ''),

                        
                        'image': base_url + '/img_restaurant/?id=' + str(r.id) if r.image_1920 else False,
                     
                        'tag_line': r.tag_line,
                        'currency': r.currency_id.name,
                        'has_tax': r.has_tax,
                        'tax_type': r.tax_type,
                        'tax_percentage': r.tax_percentage,
                        'services': ', '.join([x.name for x in r.cuisine])
        } ,request.env['res.partner'].sudo().search([('seller', '=', True),('id','=',salon_id)])))
        
        return  {'salon':salon}
    
    
    @http.route('/salon_search',type='json',auth='public')
    def salon_search(self,name):
        salons = list(map(lambda x:{

            "salon_name": x.name,
            "salon_id": x.id
        } ,request.env['res.partner'].sudo().search([('seller', '=', True),('name','ilike',name)])))
        
  
        return  {'salons':salons}
        
    @http.route('/salon_near_you', type='json', auth='public')
    def salon_near_you(self, lat, lng, lang):
        res = []
        res_open = []
        res_close = []
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        tz = pytz.timezone(request.env.user.tz) or pytz.utc

        day = pytz.utc.localize(datetime.today()).astimezone(tz).strftime('%A')
        hour = datetime.now(tz).hour
        minute = datetime.now(tz).minute
        time = float(str(hour) + '.' + str(minute))

        source = (lat, lng)

        all_res = request.env['res.partner'].sudo().with_context(lang=lang).search([('seller', '=', True)])

        for r in all_res:

            if r.res_location:

                destination = r.res_location.split(",")

                # destination = (float(destination[0]), float(destination[1]))
                try:
                    destination = (float(destination[0]), float(destination[1]))
                except ValueError:
                    continue

                distance = geodesic(source, destination).km

                # if distance and distance<30:

                open = True
                today = False

                for slots in r.timeslots:
                    if slots.name.lower() == day.lower():
                        today = self.calculate_time(slots.opening_time) + ' - ' + self.calculate_time(
                            slots.closing_time)

                        if time < slots.opening_time or time > slots.closing_time:
                            open = False
                            break
                #                     timeslots=[]
                #                     for t in r.timeslots:
                #                         timeslots.append({
                #                             'name':t.name,
                #                             'opening_time':t.opening_time,
                #                             'closing_time':t.closing_time,
                #                         })

                if not open or r.is_busy:
                    res_close.append({
                        'name': r.name,
                        'home_service': r.has_delivery,
                        'salon_service': r.has_pickup,
                        'has_qrscan': r.has_qrscan,
                        'salon_location': r.res_location,
                        'delivery_zone': r.delivery_zone,
                        #          'delivery_est':r.delivery_est,
                        'delivery_charges': r.delivery_charges,
                        'is_featured': r.is_featured,
                        'minimum_order': r.minimum_order,
                        'has_promotions': r.has_promotions,
                        # 'timeslots':timeslots,
                        'is_busy': r.is_busy,
                        'website': r.website,
                        'average_rating': r.average_rating,
                        'today': today,
                        #      'area':area.name,
                        #       'polygon':area.polygon,
                        'id': r.id,
                        'open': open,
                        'salon_address': (r.street + ' ' if r.street else '') + (r.city + ' ' if r.city else '') + (
                            r.state_id.name + ' ' if r.state_id.name else '') + (
                                             r.country_id.name if r.country_id.name else ''),

                        'distance': str(math.floor((distance / 60) * 60) + 3) + '-' + str(
                            math.floor((distance / 60) * 60) + 5) if math.floor((distance / 60) * 60) > 0 else '2-4',
                        'distance_sort': distance,
                        #  'image_medium':'data:image/png;base64,'+r.image_medium if r.image_medium else r.website+'/waiteroo_website_customer/static/description/icon.png',
                        #   'image_small':'data:image/png;base64,'+r.image_small if r.image_small else r.website+'/waiteroo_website_customer/static/description/icon.png',
                        'image': base_url + '/img_restaurant/?id=' + str(r.id) if r.image_1920 else False,
                        #       'profile_banner':'data:image/png;base64,'+str(r.profile_banner.decode("utf-8")) if r.profile_banner else False,
                        # 'image':base_url+'/web/image?model=res.partner&id='+str(r.id)+'&field=image_1920',
                        'tag_line': r.tag_line,
                        'currency': r.currency_id.name,
                        'has_tax': r.has_tax,
                        'tax_type': r.tax_type,
                        'tax_percentage': r.tax_percentage,
                        'services': ', '.join([x.name for x in r.cuisine])

                    })

                else:

                    res_open.append({
                        'name': r.name,
                        'home_service': r.has_delivery,
                        'salon_service': r.has_pickup,
                        'has_qrscan': r.has_qrscan,
                        'salon_location': r.res_location,
                        'delivery_zone': r.delivery_zone,
                        'today': today,
                        'average_rating': r.average_rating,
                        #       'delivery_est':r.delivery_est,
                        'delivery_charges': r.delivery_charges,
                        'is_featured': r.is_featured,
                        'minimum_order': r.minimum_order,
                        'has_promotions': r.has_promotions,
                        'distance': str(math.floor((distance / 60) * 60) + 3) + '-' + str(
                            math.floor((distance / 60) * 60) + 5) if math.floor((distance / 60) * 60) > 0 else '2-4',
                        'distance_sort': distance,
                        # 'timeslots':timeslots,
                        'is_busy': r.is_busy,
                        'website': r.website,
                        #     'area':area.name,
                        #     'polygon':area.polygon,
                        'id': r.id,
                        'open': open,
                        'salon_address': (r.street + ' ' if r.street else '') + (r.city + ' ' if r.city else '') + (
                            r.state_id.name + ' ' if r.state_id.name else '') + (
                                             r.country_id.name if r.country_id.name else ''),

                        #  'image_medium':'data:image/png;base64,'+r.image_medium if r.image_medium else r.website+'/waiteroo_website_customer/static/description/icon.png',
                        #   'image_small':'data:image/png;base64,'+r.image_small if r.image_small else r.website+'/waiteroo_website_customer/static/description/icon.png',
                        'image': base_url + '/img_restaurant/?id=' + str(r.id) if r.image_1920 else False,
                        #       'profile_banner':'data:image/png;base64,'+str(r.profile_banner.decode("utf-8")) if r.profile_banner else False,
                        # 'image':base_url+'/web/image?model=res.partner&id='+str(r.id)+'&field=image_1920',
                        'tag_line': r.tag_line,
                        'currency': r.currency_id.name,
                        'has_tax': r.has_tax,
                        'tax_type': r.tax_type,
                        'tax_percentage': r.tax_percentage,
                        'services': ', '.join([x.name for x in r.cuisine])

                    })

        res = sorted(res_open, key=lambda r: r['distance_sort']) + sorted(res_close, key=lambda r: r['distance_sort'])

        return res

    @http.route('/get_top_salons', type='json', auth='public')
    def get_top_salons(self, lang):
        res = []
        res_open = []
        res_close = []
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        tz = pytz.timezone(request.env.user.tz) or pytz.utc

        day = pytz.utc.localize(datetime.today()).astimezone(tz).strftime('%A')
        hour = datetime.now(tz).hour
        minute = datetime.now(tz).minute
        time = float(str(hour) + '.' + str(minute))

        all_res = request.env['res.partner'].sudo().with_context(lang=lang).search([('seller', '=', True)])

        total = 0
        for r in all_res:

            total = total + 1
            if r.res_location:

                open = True
                today = False

                for slots in r.timeslots:
                    if slots.name.lower() == day.lower():
                        today = self.calculate_time(slots.opening_time) + ' - ' + self.calculate_time(
                            slots.closing_time)

                        if time < slots.opening_time or time > slots.closing_time:
                            open = False
                            break
                #                     timeslots=[]
                #                     for t in r.timeslots:
                #                         timeslots.append({
                #                             'name':t.name,
                #                             'opening_time':t.opening_time,
                #                             'closing_time':t.closing_time,
                #                         })

                if not open or r.is_busy:
                    res_close.append({
                        'name': r.name,
                        'home_service': r.has_delivery,
                        'salon_service': r.has_pickup,
                        'has_qrscan': r.has_qrscan,
                        'salon_location': r.res_location,
                        'delivery_zone': r.delivery_zone,
                        #          'delivery_est':r.delivery_est,
                        'delivery_charges': r.delivery_charges,
                        'is_featured': r.is_featured,
                        'minimum_order': r.minimum_order,
                        'has_promotions': r.has_promotions,
                        # 'timeslots':timeslots,
                        'is_busy': r.is_busy,
                        'website': r.website,
                        'average_rating': r.average_rating,
                        'today': today,
                        #      'area':area.name,
                        #       'polygon':area.polygon,
                        'id': r.id,
                        'open': open,
                        'salon_address': (r.street + ' ' if r.street else '') + (r.city + ' ' if r.city else '') + (
                            r.state_id.name + ' ' if r.state_id.name else '') + (
                                             r.country_id.name if r.country_id.name else ''),
                        #          'distance':str(math.floor((distance/60)*60)+3)+'-'+str(math.floor((distance/60)*60)+5) if math.floor((distance/60)*60)>0 else '2-4',
                        #          'distance_sort':distance,
                        #  'image_medium':'data:image/png;base64,'+r.image_medium if r.image_medium else r.website+'/waiteroo_website_customer/static/description/icon.png',
                        #   'image_small':'data:image/png;base64,'+r.image_small if r.image_small else r.website+'/waiteroo_website_customer/static/description/icon.png',
                        'image': base_url + '/img_restaurant/?id=' + str(r.id) if r.image_1920 else False,
                        #       'profile_banner':'data:image/png;base64,'+str(r.profile_banner.decode("utf-8")) if r.profile_banner else False,
                        # 'image':base_url+'/web/image?model=res.partner&id='+str(r.id)+'&field=image_1920',
                        'tag_line': r.tag_line,
                        'currency': r.currency_id.name,
                        'has_tax': r.has_tax,
                        'tax_type': r.tax_type,
                        'tax_percentage': r.tax_percentage,
                        'services': ', '.join([x.name for x in r.cuisine])

                    })

                else:

                    res_open.append({
                        'name': r.name,
                        'home_service': r.has_delivery,
                        'salon_service': r.has_pickup,
                        'has_qrscan': r.has_qrscan,
                        'salon_location': r.res_location,
                        'delivery_zone': r.delivery_zone,
                        'today': today,
                        'average_rating': r.average_rating,
                        #       'delivery_est':r.delivery_est,
                        'delivery_charges': r.delivery_charges,
                        'is_featured': r.is_featured,
                        'minimum_order': r.minimum_order,
                        'has_promotions': r.has_promotions,
                        #           'distance':str(math.floor((distance/60)*60)+3)+'-'+str(math.floor((distance/60)*60)+5) if math.floor((distance/60)*60)>0 else '2-4',
                        #          'distance_sort':distance,
                        # 'timeslots':timeslots,
                        'is_busy': r.is_busy,
                        'website': r.website,
                        #     'area':area.name,
                        #     'polygon':area.polygon,
                        'id': r.id,
                        'open': open,
                        'salon_address': (r.street + ' ' if r.street else '') + (r.city + ' ' if r.city else '') + (
                            r.state_id.name + ' ' if r.state_id.name else '') + (
                                             r.country_id.name if r.country_id.name else ''),

                        #  'image_medium':'data:image/png;base64,'+r.image_medium if r.image_medium else r.website+'/waiteroo_website_customer/static/description/icon.png',
                        #   'image_small':'data:image/png;base64,'+r.image_small if r.image_small else r.website+'/waiteroo_website_customer/static/description/icon.png',
                        'image': base_url + '/img_restaurant/?id=' + str(r.id) if r.image_1920 else False,
                        #       'profile_banner':'data:image/png;base64,'+str(r.profile_banner.decode("utf-8")) if r.profile_banner else False,
                        # 'image':base_url+'/web/image?model=res.partner&id='+str(r.id)+'&field=image_1920',
                        'tag_line': r.tag_line,
                        'currency': r.currency_id.name,
                        'has_tax': r.has_tax,
                        'tax_type': r.tax_type,
                        'tax_percentage': r.tax_percentage,
                        'services': ', '.join([x.name for x in r.cuisine])

                    })
            if total > 20:
                break

        res_open = sorted(res_open, key=lambda r: r['average_rating'], reverse=True)
        res_close = sorted(res_close, key=lambda r: r['average_rating'], reverse=True)
        res = res_open + res_close
        return res

    #
    #         if area=='All':
    #
    #             matching = request.env['delivery.area'].sudo().search([])
    #
    #         else:
    #
    #
    #             matching = request.env['delivery.area'].sudo().search([])
    #
    #
    #             all_ref=[x.name.lower() for x in matching]
    #             to_check=area.lower().replace("'",'').split(" ")
    #             matched_area=[]
    #             for word in to_check:
    #
    #                 found=difflib.get_close_matches(word,all_ref)
    #                 if found:
    #                     matched_area=found
    #                     break
    #
    #             if len(matched_area)>0:
    #                matching = request.env['delivery.area'].sudo().with_context(lang=lang).search([('name','ilike',matched_area[0])])
    #             else:
    #                 matched_area=difflib.get_close_matches(area.lower().replace("'",''),all_ref)
    #
    #                 if len(matched_area)>0:
    #                     matching = request.env['delivery.area'].sudo().with_context(lang=lang).search([('name','ilike',matched_area[0])])
    #                 else:
    #                     return
    #
    #
    #
    #         for area in matching:
    #
    #             for r in area.restaurant:
    #                 open=True
    #                 if r.has_pickup:
    #                     for slots in r.timeslots:
    #                         if slots.name.lower()==day.lower():
    #                             if time<slots.opening_time or time>slots.closing_time:
    #                                 open=False
    #                                 break
    # #                     timeslots=[]
    # #                     for t in r.timeslots:
    # #                         timeslots.append({
    # #                             'name':t.name,
    # #                             'opening_time':t.opening_time,
    # #                             'closing_time':t.closing_time,
    # #                         })
    #
    #                     if not open or r.is_busy:
    #                         res_close.append({
    #                             'name':r.name,
    #                             'has_delivery':r.has_delivery,
    #                             'has_pickup':r.has_pickup,
    #                             'has_qrscan':r.has_qrscan,
    #                             'res_location':r.res_location,
    #                             'delivery_zone':r.delivery_zone,
    #                             'delivery_est':r.delivery_est,
    #                             'delivery_charges':r.delivery_charges,
    #                             'is_featured':r.is_featured,
    #                             'minimum_order':r.minimum_order,
    #                             'has_promotions':r.has_promotions,
    #                            # 'timeslots':timeslots,
    #                             'is_busy':r.is_busy,
    #                             'website':r.website,
    #                             'area':area.name,
    #                             'polygon':area.polygon,
    #                             'id':r.id,
    #                             'open':open,
    #                           #  'image_medium':'data:image/png;base64,'+r.image_medium if r.image_medium else r.website+'/waiteroo_website_customer/static/description/icon.png',
    #                          #   'image_small':'data:image/png;base64,'+r.image_small if r.image_small else r.website+'/waiteroo_website_customer/static/description/icon.png',
    #                           'image':base_url+'/img_restaurant/?id='+str(r.id) if r.image_1920 else False,
    #                      #       'profile_banner':'data:image/png;base64,'+str(r.profile_banner.decode("utf-8")) if r.profile_banner else False,
    #                            # 'image':base_url+'/web/image?model=res.partner&id='+str(r.id)+'&field=image_1920',
    #                             'tag_line':r.tag_line,
    #                             'currency':r.currency_id.name,
    #                             'has_tax':r.has_tax,
    #                             'tax_type':r.tax_type,
    #                             'tax_percentage':r.tax_percentage,
    #                             'cuisine': ', '.join([x.name for x in r.cuisine])
    #
    #
    #                         })
    #
    #                     else:
    #
    #                         res_open.append({
    #                             'name':r.name,
    #                             'has_delivery':r.has_delivery,
    #                             'has_pickup':r.has_pickup,
    #                             'has_qrscan':r.has_qrscan,
    #                             'res_location':r.res_location,
    #                             'delivery_zone':r.delivery_zone,
    #                             'delivery_est':r.delivery_est,
    #                             'delivery_charges':r.delivery_charges,
    #                             'is_featured':r.is_featured,
    #                             'minimum_order':r.minimum_order,
    #                             'has_promotions':r.has_promotions,
    #                            # 'timeslots':timeslots,
    #                             'is_busy':r.is_busy,
    #                             'website':r.website,
    #                             'area':area.name,
    #                             'polygon':area.polygon,
    #                             'id':r.id,
    #                             'open':open,
    #                           #  'image_medium':'data:image/png;base64,'+r.image_medium if r.image_medium else r.website+'/waiteroo_website_customer/static/description/icon.png',
    #                          #   'image_small':'data:image/png;base64,'+r.image_small if r.image_small else r.website+'/waiteroo_website_customer/static/description/icon.png',
    #                           'image':base_url+'/img_restaurant/?id='+str(r.id) if r.image_1920 else False,
    #                      #       'profile_banner':'data:image/png;base64,'+str(r.profile_banner.decode("utf-8")) if r.profile_banner else False,
    #                            # 'image':base_url+'/web/image?model=res.partner&id='+str(r.id)+'&field=image_1920',
    #                             'tag_line':r.tag_line,
    #                             'currency':r.currency_id.name,
    #                             'has_tax':r.has_tax,
    #                             'tax_type':r.tax_type,
    #                             'tax_percentage':r.tax_percentage,
    #                             'cuisine': ', '.join([x.name for x in r.cuisine])
    #
    #
    #                         })
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #         res=res_open+res_close
    #         return res

    @http.route('/get_areas', type='json', auth='public')
    def get_areas(self):
        res = []

        delivery_areas = request.env['delivery.area'].sudo().search([])

        states = request.env['res.country.state'].sudo().search(
            [('country_id', '=', request.env.user.partner_id.country_id.id)])

        for state in states:

            main_temp = []

            for area in delivery_areas:

                if state.name == area.state.name:
                    temp = {

                        'area': area.name,

                    }

                    main_temp.append(temp)

            res.append({'title': state.name, 'data': main_temp, 'count': len(main_temp)})

        return res

    @http.route('/get_cuisines', type='json', auth='public')
    def get_cuisines(self, lang):

        res = []
        cuisines = request.env['restaurant.cuisine'].sudo().with_context(lang=lang).search([], order='name asc')

        for cuisine in cuisines:
            res.append({
                'name': cuisine.name,
                'selected': False
            })

        return res

    @http.route('/sendnotifications', type='json', auth='public')
    def sendnotifications(self, r_id, order_id, msg):

        waiteroo_notification = request.env['waiteroo.notification'].sudo().create({

            'restaurant': r_id,
            'order_id': order_id,
            'name': msg,

        })

        if waiteroo_notification.restaurant.website:
            payload = {"jsonrpc": "2.0",
                       "params": {"order_id": waiteroo_notification.order_id.client_order_ref, "msg": msg}}
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", waiteroo_notification.restaurant.website + 'sendnotificationsapi',
                                        headers=headers, data=json.dumps(payload))
            # create recordd in waiteroo notificaitons

        # if restaurant.website:

        # sync with restaurant pos
        #            print('')

        return

    @http.route(['/getnotifications', '/api/getnotifications'], type='json', auth='public')
    def getnotifications(self, r_id, last_id):

        if last_id:

            new_order_notification = request.env['waiteroo.notification'].sudo().search([('restaurant.id', '=', r_id)],
                                                                                        limit=1)

            if new_order_notification.id == last_id:
                return
        waiteroo_notification = request.env['waiteroo.notification'].sudo().search([('restaurant.id', '=', r_id)],
                                                                                   limit=80)

        res = []

        for notification in waiteroo_notification:
            res.append({
                'id': notification.id,
                'name': notification.name,
                'order_id': notification.order_id.name
            })

        return res

    @http.route('/get_salon_review', type='json', auth='public')
    def get_salon_review(self, r_id, lang):
        res = []
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        salon_reviews = request.env['seller.review'].sudo().with_context(lang=lang).search(
            [('marketplace_seller_id', '=', r_id)])
        tz = pytz.timezone(request.env.user.tz) or pytz.utc

        for review in salon_reviews:
            temp = {

                "customer_name": review.partner_id.name,
                "customer_image": base_url + '/img_restaurant/?id=' + str(
                    review.partner_id.id) if review.partner_id.image_1920 else False,
                "review_title": review.title,
                "review_message": review.msg,
                "review_date": pytz.utc.localize(review.create_date).astimezone(tz).strftime("%d/%m/%Y"),
                "rating": review.rating
            }

            res.append(temp)

        return {'reviews': res}

    @http.route('/get_top_specialist', type='json', auth='public')
    def get_top_specialist(self, lang):
        res = []
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        specialists = request.env['salon.employee'].sudo().with_context(lang=lang).search([])

        for employee in specialists:
            res.append({
                "id": employee.id,
                "image": base_url + '/salon_employee_img/?id=' + str(employee.id) if employee.image_1920 else False,
                "name": employee.name,
                "rating": employee.employee_average_rating,
                "salon": {'salon_id': employee.salon_id.id, 'salon_name': employee.salon_id.name},
                "department": employee.department_id.name,
                "employee_reviews": [{
                    'id': review.id,
                    'name': review.customer.name,
                    'rating': review.rating,
                    'comment': review.title
                } for review in employee.employee_ratings],
                "services": [{
                    'id': product.id,
                    'name': product.name,
                    'price': product.lst_price,
                    'image': base_url + '/img_product/?id=' + str(product.id) if product.image_1920 else False,
                    'currency': product.currency_id.name,
                    'service_time': product.service_time

                } for product in employee.service_products]
            })

        res = sorted(res, key=lambda r: r['rating'], reverse=True)
        return res

    @http.route('/get_salon_specialist', type='json', auth='public')
    def get_salon_specialist(self, r_id, lang):
        res = []
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        restaurant = request.env['res.partner'].sudo().with_context(lang=lang).search([('id', '=', r_id)])
        all_depart = request.env['salon.department'].sudo().with_context(lang=lang).search([])
        for department in all_depart:

            department_dict = []
            for employee in restaurant.salon_employees:

                if department.id == employee.department_id.id:
                    temp = {
                        "id": employee.id,
                        "image": base_url + '/salon_employee_img/?id=' + str(
                            employee.id) if employee.image_1920 else False,
                        "name": employee.name,
                        "department": employee.department_id.name,
                        "employee_reviews": [{
                            'id': review.id,
                            'name': review.customer.name,
                            'rating': review.rating,
                            'comment': review.title
                        } for review in employee.employee_ratings],
                        "services": [{
                            'id': product.id,
                            'name': product.name,
                            'price': product.lst_price,
                            'image': base_url + '/img_product/?id=' + str(product.id) if product.image_1920 else False,
                            'currency': product.currency_id.name,
                            'service_time': product.service_time

                        } for product in employee.service_products]
                    }
                    department_dict.append(temp)
            if (department_dict.__len__() > 0):
                res.append({department.name: department_dict})

        return {'specialist': res}

    @http.route('/get_salon_gallery', type='json', auth='public')
    def get_salon_gallery(self, r_id, lang):
        res = []
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        restaurant = request.env['res.partner'].sudo().with_context(lang=lang).search([('id', '=', r_id)])

        for i in restaurant.salon_gallery:
            temp = {
                "image": base_url + '/salon_gallery/?id=' + str(i.id)
            }
            res.append(temp)

        return {'gallery': res}

    @http.route('/get_salon_about', type='json', auth='public')
    def get_salon_about(self, r_id, lang):
        res = []

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        restaurant = request.env['res.partner'].sudo().with_context(lang=lang).search([('id', '=', r_id)])

        tz = pytz.timezone(request.env.user.tz) or pytz.utc

        day = pytz.utc.localize(datetime.today()).astimezone(tz).strftime('%A')
        hour = datetime.now(tz).hour
        minute = datetime.now(tz).minute
        time = float(str(hour) + '.' + str(minute))

        for r in restaurant:

            # print("here--",area)

            # area=[x for x in r.delivery_areas if x.name == area]

            open = True
            today = False

            for slots in r.timeslots:
                if slots.name.lower() == day.lower():
                    today = self.calculate_time(slots.opening_time) + ' - ' + self.calculate_time(slots.closing_time)
                    if time < slots.opening_time or time > slots.closing_time:
                        open = False
                        break

            timeslots = []
            for t in r.timeslots:
                timeslots.append({
                    'name': t.name.upper(),
                    'opening_time': self.calculate_time(t.opening_time),
                    'closing_time': self.calculate_time(t.closing_time),
                })

            res.append({
                'name': r.name,
                'home_service': r.has_delivery,
                'salon_service': r.has_pickup,
                'salon_address': (r.street + ' ' if r.street else '') + (r.city + ' ' if r.city else '') + (
                    r.state_id.name + ' ' if r.state_id.name else '') + (
                                     r.country_id.name if r.country_id.name else ''),
                'has_qrscan': r.has_qrscan,
                'salon_location': r.res_location,
                'contact': r.phone,
                'information': r.profile_msg if r.profile_msg != "<p><br></p>" else False,
                'is_featured': r.is_featured,
                'minimum_order': r.minimum_order,
                'has_promotions': r.has_promotions,
                'today': today,
                'timeslots': timeslots,
                'is_busy': r.is_busy,
                'website': r.website,
                #   'area':area,
                'polygon': False,
                'id': r.id,
                'open': open,
                #  'image_medium':'data:image/png;base64,'+r.image_medium if r.image_medium else r.website+'/waiteroo_website_customer/static/description/icon.png',
                #   'image_small':'data:image/png;base64,'+r.image_small if r.image_small else r.website+'/waiteroo_website_customer/static/description/icon.png',
                'image': base_url + '/img_restaurant/?id=' + str(r.id) if r.image_1920 else False,
                'profile_banner': 'data:image/png;base64,' + str(
                    r.profile_banner.decode("utf-8")) if r.profile_banner else False,
                # 'image':base_url+'/web/image?model=res.partner&id='+str(r.id)+'&field=image_1920',
                'tag_line': r.tag_line,
                'currency': r.currency_id.name,
                'has_tax': r.has_tax,
                'tax_type': r.tax_type,
                'tax_percentage': r.tax_percentage,
                'services': ', '.join([x.name for x in r.cuisine])

            })

        return res

    @http.route('/get_res_banner', type='json', auth='public')
    def get_res_banner(self, r_id):

        restaurant = request.env['res.partner'].sudo().search([('id', '=', r_id)])

        return {'profile_banner': 'data:image/png;base64,' + str(
            restaurant.profile_banner.decode("utf-8")) if restaurant.profile_banner else False}

    @http.route(['/check_user', '/api/check_user'], type='json', auth='public')
    def check_user(self, email, password):

        user_id = request.env['res.users'].sudo()._login('waiteroo_vendor_place', email, password)

        if user_id:
            user = request.env['res.users'].sudo().search([('id', '=', user_id)])
            return {'r_id': user.partner_id.id}

    @http.route(['/change_res_state', '/api/change_res_state'], type='json', auth='public')
    def change_res_state(self, r_id, is_busy):

        restaurant = request.env['res.partner'].sudo().search([('id', '=', r_id)])

        restaurant.sudo().write({'is_busy': is_busy})

    @http.route(['/get_res_state', '/api/get_res_state'], type='json', auth='public')
    def get_res_state(self, r_id):

        restaurant = request.env['res.partner'].sudo().search([('id', '=', r_id)])
        return {'is_busy': restaurant.is_busy}

    @http.route('/offline', type='http', auth='public', website=True)
    def offline(self):

        return """<h1 style="text-align:center;margin-top: 250px">You are  Offline</h1>"""

    def send_push_message(self, token, title, message, extra=None):

        # print("Here push tocke",token)
        try:
            response = PushClient().publish(
                PushMessage(to=token,
                            title=title,
                            body=message,
                            sound="default",
                            badge=0,
                            channel_id="order-notification",
                            data=extra))
        except PushServerError as exc:
            # Encountered some likely formatting/validation error.
            rollbar.report_exc_info(
                extra_data={
                    'token': token,
                    'message': message,
                    'extra': extra,
                    'errors': exc.errors,
                    'response_data': exc.response_data,
                })
            pass
        except (ConnectionError, HTTPError) as exc:
            # Encountered some Connection or HTTP error - retry a few times in
            # case it is transient.
            rollbar.report_exc_info(
                extra_data={'token': token, 'message': message, 'extra': extra})
            # raise self.retry(exc=exc)
            pass
        try:
            # We got a response back, but we don't know whether it's an error yet.
            # This call raises errors so we can handle them with normal exception
            # flows.
            response.validate_response()
        except DeviceNotRegisteredError:
            # Mark the push token as inactive
            # from notifications.models import PushToken
            # PushToken.objects.filter(token=token).update(active=False)
            pass
        except PushResponseError as exc:
            # Encountered some other per-notification error.
            rollbar.report_exc_info(
                extra_data={
                    'token': token,
                    'message': message,
                    'extra': extra,
                    'push_response': exc.push_response._asdict(),
                })
            # raise self.retry(exc=exc)
            pass

