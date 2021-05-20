# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
import json

class Main(http.Controller):
    
    @http.route(['/api/get_vehicles/'], type="json", methods=['POST'], auth="public",  csrf=False)
    def get_vehicles(self):
        veh = request.env['vehicle.vehicle'].sudo().search([])
        vList = list(map(lambda x : {
            "id": x.id,
            "vehicle_id": x.vehicle_id,
            "name": x.vehicle_name,
            "company": x.vehicle_company,
            "modal": x.vehicle_modal,
            "type": x.vehicle_type,
            "tyre": list(map(lambda y :{
                "id":y.id,
                "name":y.name,
                "company":y.company,
                "notes":y.notes,
            },x.vehicle_tires))[0]
        }, veh))
        return vList
        
    @http.route(['/api/get_vehicle_by_id/'], type="json", methods=['POST'], auth="public",  csrf=False)
    def get_vehicle_by_id(self, id):
        veh = request.env['vehicle.vehicle'].sudo().search([('id', '=', id)])
        vList = list(map(lambda x : {
            "id": x.id,
            "vehicle_name": x.vehicle_name,
            "vehicle_company": x.vehicle_company,
            "vehicle_modal": x.vehicle_modal,
            "vehicle_type": x.vehicle_type,
        }, veh))
        return vList
    
    @http.route(['/api/add_vehicle/'], type="json", methods=['POST'], auth="public",  csrf=False)
    def add_vehicle(self, vehicle_name, vehicle_company, vehicle_modal, vehicle_type):
        new_record = {
            "vehicle_name": vehicle_name,
            "vehicle_company": vehicle_company,
            "vehicle_modal": vehicle_modal,
            "vehicle_type": vehicle_type,
        }
        veh = request.env['vehicle.vehicle'].sudo().create(new_record)

        return { "msg":"New record added!" }

    @http.route(['/api/update_vehicle/'], type="json", methods=['POST'], auth="public",  csrf=False)
    def update_vehicle(self, **data):
        if data["id"] == False:
            return { "msg":"Vehicle id is required" }
        prev_record = request.env['vehicle.vehicle'].sudo().search( [('id', '=', data['id'])])
        if prev_record:
            prev_record.sudo().write({
                "vehicle_name": data["vehicle_name"],
                "vehicle_company": data["vehicle_company"],
                "vehicle_modal": data["vehicle_modal"],
                "vehicle_type": data["vehicle_type"],
            })
        else:
            return { "msg":"Vehicle id not found" }
        return { "msg":"Record updated!" }

    @http.route(['/api/delete_vehicle/'], type="json", methods=['POST'], auth="public",  csrf=False)
    def delete_vehicle(self, id):
        if id == False:
            return { "msg":"Vehicle id is missing" }
        record = request.env['vehicle.vehicle'].sudo().search( [('id', '=', id)])
        record.unlink()
        return { "msg":"Record deleted!" }