# -*- coding: utf-8 -*-

import ast

from datetime import date, datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class MaintenanceRequest(models.Model):
    _name = 'maintenance.request'
    _inherit = 'maintenance.request'
    _description = 'Maintenance Request'
    _order = "id desc"
    _check_company_auto = True

    @api.model_create_multi
    def create(self, vals_list):        
        maintenance_requests = super().create(vals_list)
        return maintenance_requests

    def write(self, vals):       
        res = super(MaintenanceRequest, self).write(vals)        
        return res
