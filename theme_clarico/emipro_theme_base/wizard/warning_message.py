# -*- coding: utf-8 -*-
"""
    This model is used to create a for upgrade the theme after click on the apply button of model.
"""
from odoo import models, fields, api, _


class WarningMessage(models.TransientModel):
    _name = "warning.message"

    def process(self):
        """
            Refresh the current theme of the current website.

            To refresh it, we only need to upgrade the modules.
            Indeed the (re)loading of the theme will be done automatically on ``write``.
        """
        website = self.env['website'].get_current_website()
        website.theme_id._theme_upgrade_upstream()
