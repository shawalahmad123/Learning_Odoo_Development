from odoo import models, fields, api, _
from odoo.tools.translate import _
from odoo.exceptions import UserError


import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mp_auto_timeslot_approve=fields.Boolean(string='Auto Timeslot Approve',default=False)
    mp_auto_plan_approve = fields.Boolean(string='Auto Plan Approve', default=False)

class BookingPlanExtend(models.Model):
    _inherit = "booking.plan"

    state=fields.Selection([("new","New"),("pending","Pending"), ("approved","Approved") ,("rejected","Rejected")], default="new")
    marketplace_seller_id = fields.Many2one(
        "res.partner", string="Seller", default=lambda
            self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else
        self.env['res.partner'], copy=False, track_visibility='onchange',
        )


class BookingTimeSlotExtend(models.Model):
    _inherit = "booking.time.slot"

    state=fields.Selection([("new","New"),("pending","Pending"), ("approved","Approved") ,("rejected","Rejected")], default="new")
    marketplace_seller_id = fields.Many2one(
        "res.partner", string="Seller", default=lambda
            self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else
        self.env['res.partner'], copy=False, track_visibility='onchange',
    )

