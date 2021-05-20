# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ir_module_module(models.Model):
    _inherit = "ir.module.module"
    
    def button_refresh_theme(self):
        """
        It's call while update the Emipro theme and give a warning message to user in model window.
        """
        if self.author == "Emipro Technologies Pvt. Ltd.":
            view = self.env.ref('emipro_theme_base.warning_message_ept')
            return {
                'type': 'ir.actions.act_window',
                'name': ('Warning'),
                'res_model': 'warning.message',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view.id,
                'views': [(view.id, 'form')],
                'target': 'new',
                'context': {'cancel_id': self.id},
                'nodestroy': True,
            }
                