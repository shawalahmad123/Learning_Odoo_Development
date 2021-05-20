# -*- coding: utf-8 -*-


from odoo import models, fields,api
import qrcode
from PIL import Image
import base64
from io import BytesIO
from exponent_server_sdk import DeviceNotRegisteredError
from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage
from exponent_server_sdk import PushResponseError
from exponent_server_sdk import PushServerError
from odoo.modules.module import get_module_resource
class WaiterooOrder(models.Model):
    _name = 'waiteroo.order'
    _description = 'Waiteroo Orders'

    
    customer = fields.Many2one('res.partner',string='Customer',domain="[('seller','=', True)]")
    restaurant = fields.Many2one('res.partner',string='Restaurant',domain="[('seller','=', True)]")
    total = fields.Float(string='Total',digits=0)
    status = fields.Selection([
        ('new', 'New'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('inprogress', 'In Progress'),
        ('completed', 'Completed'),
        
    ], string='Status',default='new')
    order = fields.Text(string='Order Data')

class WaiterooAreaLog(models.Model):
    _name = 'waiteroo.area.log'
    _description = 'Waiteroo Area Logs'

    
    name=fields.Char(string='Area')
    city=fields.Char(string='City / State')
    country=fields.Char(string='Country')
    

class WaiterooPublicNotification(models.Model):
    _name = 'waiteroo.public.notification'
    _description = 'Waiteroo Public Notification'

    
    name=fields.Char(string='Expo Token')
    
    
    
    
    
    
    def send_notification(self,title,message):
        
        records=self.env['waiteroo.public.notification'].search([])
        for rec in records:
            self.send_push_message(rec.name,title,message)
            
    
    
    def send_push_message(self,token,title, message, extra=None):
        
        #print("Here push tocke",token)
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
            #raise self.retry(exc=exc)
            pass
        try:
            # We got a response back, but we don't know whether it's an error yet.
            # This call raises errors so we can handle them with normal exception
            # flows.
            response.validate_response()
        except DeviceNotRegisteredError:
            # Mark the push token as inactive
            #from notifications.models import PushToken
            #PushToken.objects.filter(token=token).update(active=False)
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
            #raise self.retry(exc=exc)
            pass

      


class CustomerAddress(models.Model):
    _name = 'customer.address'
    _description = 'Waiteroo Customer Address'


    name = fields.Char(string='Type')
    place_name = fields.Char(string='Place Name')
    place_coordinates = fields.Char(string='Coordinates')
    
    customer = fields.Many2one('res.partner', string='Customer',domain="[('seller','=', True)]")
    
class DeliveryArea(models.Model):
    _name = 'delivery.area'
    _description = 'Delivery Zones'


    name = fields.Char(string='Area')
    polygon = fields.Char(string='Polygon')
    restaurant = fields.Many2many('res.partner', string='Salon',domain="[('seller','=', True)]")
    state = fields.Many2one('res.country.state', string='State')
    country = fields.Many2one('res.country', string='Country')


class WaiterooNotification(models.Model):
    _name = 'waiteroo.notification'
    _description = 'Waiteroo Notification'
    _order = 'id desc'
    state = fields.Selection([
        ('unread', 'Unread'),
        ('read', 'Read'),
    ], string='State',default='unread')


    restaurant = fields.Many2one('res.partner', string='Salon',domain="[('seller','=', True)]")
    order_id=fields.Many2one('sale.order',string='Order',domain="[('related_seller','=', restaurant)]")
    name=fields.Char(string='Message')
    #target=fields.Char(string='Target')






class RestaurantTime(models.Model):
    _name = 'restaurant.time'
    _description = 'Salon Timings'

    name = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ], string='Day',default='monday')

    opening_time = fields.Float(string='Opening Time')
    closing_time = fields.Float(string='Closing Time')
    restaurant = fields.Many2one('res.partner', string='Salon',domain="[('seller','=', True)]")


class RestaurantTable(models.Model):
    _name = 'restaurant.table'
    _description = 'Salon Chairs'

    name = fields.Char(string="Table")

class RestaurantCuisine(models.Model):
    _name = 'restaurant.cuisine'
    _description = 'Salon Services'

    name = fields.Char(string="Services")


class SalonGallery(models.Model):
    _name='salon.gallery'
    _description='Salon Gallery'

    image=fields.Binary(string="Image", attachement=True,required=True)
    salon_id=fields.Many2one('res.partner', string='Salon',domain="[('seller','=', True)]")


class SalonEmployeeDepartment(models.Model):
    _name = 'salon.department'
    _description='Salon Employees Department'


    name = fields.Char('Department Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)


class SalonSpecialistRating(models.Model):
    _name = 'salon.employee.rating'
    _description='Salon Employees Ratings'


    rating=fields.Float(string='Rating')
    title=fields.Char(string='Title')
    customer=fields.Many2one('res.partner',string='Customer')
    employee_id=fields.Many2one('salon.employee', string='Related Specialist')



class SalonSpecialist(models.Model):
    _name = 'salon.employee'
    _description='Salon Employees'
    

    def _get_rating(self):
        """ """

        average=0
        tr=0
        tc=0
        for rating in self.employee_ratings:
            tc=tc+1
            tr=tr+rating.rating

        
        if tc>0:
            average=tr/tc

        self.employee_average_rating=average

            


    @api.model
    def _default_image(self):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())
    
    name=fields.Char('Employee Name',required=True)
    job_title = fields.Char("Job Title")
    is_active=fields.Boolean('Is Active',default=True)
    image_1920 = fields.Image('Image',default=_default_image)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    department_id = fields.Many2one('salon.department', 'Department', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    employee_average_rating=fields.Float(compute="_get_rating",string="Rating")
    employee_ratings=fields.Many2many('salon.employee.rating',string='Employee Ratings',domain="[('employee_id.id','=',id)]")

    salon_id=fields.Many2one('res.partner', string='Salon',domain="[('seller','=', True)]")
    service_products=fields.Many2many('product.template',string='Related Service Products',domain="[(id,'in','related_specialist'),('status','=','approved')]")

class Product_Template(models.Model):
    _inherit = 'product.template'


    
    #@api.onchange('marketplace_seller_id')
    # def _getMappedEmployees(self):
        
        
    #     for record in self:

    #         return {'domain': {'related_specialist': [('id','in',[x.id for x in record.marketplace_seller_id.salon_employees])]}}
        

          
            
        

        

    service_time=fields.Float(string='Service Time in Mins',required=True,default=30)
    related_specialist=fields.Many2many('salon.employee', string='Related Specialist',domain="[('salon_id.id','=',marketplace_seller_id),('is_active','=',True)]",required=True)
    is_offer=fields.Boolean(string='Is Offer',default=False)
    offer_products=fields.Many2many('product.product',string='Offer Products',domain="[('marketplace_seller_id.id','=',marketplace_seller_id),('status','=','approved')]")

    discount_percentage=fields.Integer(string='Discount Percentage %',default=0)



    @api.onchange('offer_products','discount_percentage')
    def calculate_discount_price(self):

        total=0
        for products in self.offer_products:
            total=total+products.lst_price


        if self.discount_percentage>0:

            total=total-(total*(self.discount_percentage/100))

        
        self.lst_price=total


class res_partner(models.Model):
    _inherit = 'res.partner'


    
    def write(self,vals):


        res=super(res_partner,self).write(vals)

        salon_employees=self.env['salon.employee'].sudo().search([('salon_id.id','=',self.id)])

        for all in salon_employees:
            all.write({
                'is_active':False
            })

        for employee in self.salon_employees:

            employee.write({
                'is_active':True
            })

        return res

        



    @api.depends('has_delivery')
    def get_delivery_link(self):
        
        for rec in self._origin:
            
            if rec.has_delivery:
                rec.delivery_link='https://guest.waiteroo.com/qrscan?qr_menu_id='+str(rec.id)+'&target=Delivery'
            else:
                rec.delivery_link=False
    
    @api.depends('has_pickup')
    def get_pickup_link(self):
        
        for rec in self._origin:
            
            if rec.has_pickup:
                rec.pickup_link='https://guest.waiteroo.com/qrscan?qr_menu_id='+str(rec.id)+'&target=Pickup'
            else:
                rec.pickup_link=False
    
    def get_carhop_image(self):


        for rec in self:


            logo = Image.open(BytesIO(base64.b64decode(rec.image_1920)))
            background = Image.new('RGBA', logo.size, (255, 255, 255))
            background.paste(logo, logo)
            logo = background.convert('RGB')
            wpercent = (120 / float(logo.size[0]))
            hsize = int((float(logo.size[1]) * float(wpercent)))
            logo = logo.resize((120, hsize), Image.ANTIALIAS)
            qr_big = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                border=0
            )
            qr_big.add_data('https://guest.waiteroo.com/qrscan?qr_menu_id=%s&target=Carhop'%(rec.id))
            qr_big.make()
            img_qr_big = qr_big.make_image(fill_color="#DA291C", back_color="white").convert('RGB')
            pos = ((img_qr_big.size[0] - logo.size[0]) // 2, (img_qr_big.size[1] - logo.size[1]) // 2)
            img_qr_big.paste(logo, pos)

            # print("image",img_qr_big)
            # img_qr_big.save('output.png')

            buffered = BytesIO()
            img_qr_big.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue())

            return  str(img_str)[2:]

            #print("res image",rec.image_1920)


        #return False



    name = fields.Char(index=True,translate=True)
    
    #Client Settings -------------------------------------------------------------------------
    
    #waiteroo_client=fields.Boolean(string='Waiteroo Client')
    waiteroo_customer=fields.Boolean(string='Salon Customer')
    is_featured=fields.Boolean(string='Is Featured')
    has_delivery=fields.Boolean(string='Has Home Service')
    has_pickup=fields.Boolean(string='Has Salon Service')
    has_qrscan=fields.Boolean(string='Has QR Scan Enabled')
    #has_pos=fields.Boolean(string='Has POS')

    res_location = fields.Char(string="Salon Location")
    tag_line=fields.Char(string="Tag Line",translate=True)
    delivery_zone = fields.Char(string="Delivery Zone")

    delivery_areas = fields.Many2many('delivery.area', string='Delivery Areas')
    
    related_service_product = fields.Many2one('product.product', string='Service Product')
    
    is_busy=fields.Boolean(string='Is Busy',default=False)

    
    timeslots = fields.Many2many('restaurant.time', string='Time Slots',domain="[('restaurant.id','=',id)]")


    minimum_order = fields.Float(string="Minimum Order",default=0)
    delivery_est = fields.Float(string="Prepration Time Estimation in minutes",default=0)
    delivery_charges = fields.Float(string="Delivery Charges",default=0)
    
    has_tax=fields.Boolean(string='Has Tax',default=False)
    tax_type =fields.Selection([('Inclusive', 'Inclusive'), ('Exclusive', 'Exclusive')],default='Inclusive')
    tax_percentage=fields.Float(string='Tax Percentage')

    #promotions 
    has_promotions=fields.Boolean(string='Has Promotions')


    
    client_notification_token = fields.Char(string="Notification Token")
    
    

    #Customer Settings -------------------------------------------------------------------------------------------------------
    

    customer_notification_token = fields.Char(string="Notification Token")
    # favourite_restaurants=fields.Many2many(string="Favourite Restaurants",related='ids',domain="[('waiteroo_client','=', True)]")
    favourite_restaurants=fields.Text(string="Favourite Salons")
    waiteroo_credits=fields.Float(string='Salon Credits',default=0)
    gender=fields.Selection([('male','Male'),('female','Female')])

    addresses = fields.Text(string='Customer Address')



    #dine configuration

    tables=fields.Many2many('restaurant.table',string='Salon Chairs')

    #cusinses

    cuisine = fields.Many2many('restaurant.cuisine', string='Services')
    
    delivery_link=fields.Char(string='Home Link',compute='get_delivery_link',store=True)
    pickup_link=fields.Char(string='Salon Link',compute='get_pickup_link',store=True)
    
    
    salon_gallery = fields.Many2many('salon.gallery', string='Salon Gallery',domain="[('salon_id.id','=',id)]") 
    salon_employees=fields.Many2many('salon.employee',string='Salon Specialist',domain="[('salon_id.id','=',id)]")
