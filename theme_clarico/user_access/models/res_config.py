

from odoo import fields, models, tools, api, _

class res_config(models.TransientModel):
    _inherit = "res.config.settings"

    email_domain = fields.Char(string='Set User Domain',related='website_id.email_domain', readonly=False, translate=True)