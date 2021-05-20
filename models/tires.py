# -*- coding: utf-8 -*-

from odoo import models, fields

class Tires(models.Model):
    _name = 'vehicle.tyre'
    _description = 'Tyres'
    _rec_name='name'
    _order = 'name asc'

    name = fields.Char("Name", required=True)
    company = fields.Text("Company", required=True)
    notes = fields.Text("Notes")
    image = fields.Binary("Image")

    def write(self, vals):
        print("Before calling base")
        veh = super(Tires, self).write(vals)
        print(vals)
        print("After calling base")
        return veh

