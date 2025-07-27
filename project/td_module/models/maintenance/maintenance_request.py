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

    date_start = fields.Date(string=u'Ngày bắt đầu',
        default=lambda self: fields.Date.to_string(date.today()))
    date_end = fields.Date(string=u'Ngày hoàn thành',
        default=lambda self: fields.Date.to_string(date.today()))
    maintenance_checklist_id = fields.Many2one('maintenance.checklist', string='Cấp bảo dưỡng')
    date_repair = fields.Date(string=u'Ngày xảy ra sự cố')
    technical_spec = fields.Char(string=u'Thông số kỹ thuật')
    uom_id = fields.Many2one('uom.uom', 'Đơn vị')
    quantity = fields.Float(u'Số lượng')
    result = fields.Char(u'Kết quả')
    final_settlement_line_ids = fields.One2many('maintenance.final.settlement.line', 'maintenance_request_id', string=u'Final Settlement Line')

    @api.model_create_multi
    def create(self, vals_list):        
        maintenance_requests = super().create(vals_list)
        return maintenance_requests

    def write(self, vals):       
        res = super(MaintenanceRequest, self).write(vals)        
        return res
