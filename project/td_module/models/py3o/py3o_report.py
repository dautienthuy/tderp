# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import base64
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class Py3oReport(models.TransientModel):
    _inherit = "py3o.report"
    _name = "py3o.report"

    def create_report(self, res_ids, data):
        if data and data['context']:
            context = data['context']
            if context.get("wizard_report", False) and not res_ids:
                res_ids = context.get("active_ids", [])
        res = super(Py3oReport, self).create_report(res_ids, data)
        return res
