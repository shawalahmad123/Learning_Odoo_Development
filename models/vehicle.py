# -*- coding: utf-8 -*-

from odoo import models, fields
import random

class Vehicle(models.Model):
    _name = 'vehicle.vehicle'
    _description = 'Vehicles'
    _rec_name='vehicle_name'
    _order = 'vehicle_name asc'

    vehicle_id = fields.Char("Vehicle Id", required=True)
    vehicle_name = fields.Char("Name", required=True)
    vehicle_type = fields.Char("Type", required=True)
    vehicle_wheels = fields.Integer("Wheels")
    vehicle_tires = fields.Many2one('vehicle.tyre', 'Tires', ondelete='cascade', required=True)
    user_id = fields.Many2one('res.users', 'User', ondelete='cascade', index=True)
    vehicle_modal = fields.Char("Modal", required=True)
    vehicle_company = fields.Text("Company")
    vehicle_notes = fields.Text("Notes")
    vehicle_image = fields.Binary("Image")

    def write(self, vals):
        data = vals
        data["vehicle_id"] = random.randint(100000, 999999)
        res = super(Vehicle, self).write(vals)
        return res

