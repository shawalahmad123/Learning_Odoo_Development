

from odoo import api, fields, models, http, tools, _

class Website(models.Model):
    _inherit = "website"

    email_domain = fields.Char(string='Set Email Domain', readonly=False, translate=True,help="Set the user email which you want to register in this website")