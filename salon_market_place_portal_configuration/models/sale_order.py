# -*- coding: utf-8 -*-


from odoo import models, fields,api




class Sale_Order_line(models.Model):
    _inherit='sale.order.line'

    related_specialist=fields.Many2one('salon.employee', string='Related Specialist')


class Sale_Order(models.Model):
    _inherit = 'sale.order'
    
    
    
    pos_order=fields.Boolean(string='Pos Order',default=False)
    pos_order_json=fields.Text(string='Pos Order JSON')
    related_seller = fields.Many2one('res.partner', string='Related Salon',domain="[('seller','=', True)]")
    state = fields.Selection(selection_add=[('accepted','Accepted'),('completed','Completed'),('rejected','Rejected')])
    r_comments=fields.Text(string='Salon Comments')
    
    #related_specialist=fields.Many2one('hr.employee', string='Related Specialist',domain="[('salon_id.id','=',related_seller)]")
    service_type = fields.Selection([('home_service','Home Service'),('salon_service','Salon Service')])
    appointment_date=fields.Date(string='Appointment Date',default=fields.Date.today())
    user_location_url=fields.Char(string='Google Map location')
    booking_start_time=fields.Float(string='Appointment Start Time')
    booking_end_time=fields.Float(string='Appointment End Time')
    

    def get_customer_location_google_maps(self):
        
       
        if self.user_location_url:
            
             return { 'name'     : 'Google Maps Location',
                  'res_model': 'ir.actions.act_url',
                  'type'     : 'ir.actions.act_url',
                  'target'   : 'blank',
                  'url'      : self.user_location_url
               }
    
    #waiteroo_order = fields.Char(string='Waiteroo Order',readonly=True, copy=False, default='/')
    
    @api.model
    def create(self, vals):
        
        
        
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('waiteroo.code') or '/'
        return super(Sale_Order, self).create(vals)
    
    
    
    
    

 
    


