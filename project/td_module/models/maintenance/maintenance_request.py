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

    code = fields.Char(u'Mã nội bộ')
    date_start = fields.Date(string=u'Ngày bắt đầu',
        default=lambda self: fields.Date.to_string(date.today()))
    date_end = fields.Date(string=u'Ngày hoàn thành',
        default=lambda self: fields.Date.to_string(date.today()))
    maintenance_checklist_id = fields.Many2one('maintenance.checklist', string='Cấp bảo dưỡng')
    date_repair = fields.Date(string=u'Ngày xảy ra sự cố')
    technical_spec = fields.Char(string=u'Thông số kỹ thuật')
    uom_id = fields.Many2one('uom.uom', 'Đơn vị')
    quantity = fields.Float(u'Số lượng')
    unit_price = fields.Float(u'Đơn giá')
    amount = fields.Float(u'Thành tiền')
    result = fields.Char(u'Kết quả')
    final_settlement_line_ids = fields.One2many('maintenance.final.settlement.line', 'maintenance_request_id', string=u'Final Settlement Line')
    detail_ids = fields.One2many('maintenance.detail', 'maintenance_request_id', string=u'Detail')
    order_id = fields.Many2one('sale.order', string=u'Sale Order')
    last_working_day = fields.Date(string=u'Ngày làm việc gần nhất')
    employee_id = fields.Many2one('hr.employee',  u'Kỹ thuật viên')
    number_maintenance = fields.Integer(u'Số lần BT/BD')
    #
    backlog_status = fields.Selection([
        ('01', 'Bảo hành'),
        ('02', 'Gia hạn bảo hành'),
        ('03', 'Bảo trì'),
        ('04', 'BT Free'),
        ('05', 'Dừng BH, BT'),
        ('06', 'Tạm dừng'),
        ('07', 'Thang mới'),
        ('08', 'Khác'),
    ], string=u"Hạng mục", default='01')
    backlog_note = fields.Text("Ghi chú")
    #
    target_line_id = fields.Many2one("maintenance.target.line", string="Chỉ tiêu")
    week_in_month = fields.Integer("Tuần")

    @api.model_create_multi
    def create(self, vals_list):
        # We generate a standard reference
        for vals in vals_list:
            vals['code'] = self.env['ir.sequence'].next_by_code('maintenance.request') or '/'
        res = super().create(vals_list)
        #
        if res.user_id and res.request_date:
            week_in_month = (res.request_date.day - 1) // 7 + 1
            res.week_in_month = week_in_month
            #
            d = fields.Date.to_date(res.request_date)
            monthly = self.env["maintenance.target"].search([
                ("month", "=", d.month),
                ("year", "=", d.year),
            ], limit=1)
            if monthly:
                line = self.env["maintenance.target.line"].search([
                    ("monthly_id", "=", monthly.id),
                    ("user_id", "=", res.user_id.id)
                ], limit=1)
                if line:
                    res.target_line_id = line.id
        return res

    def write(self, vals):
        res = super(MaintenanceRequest, self).write(vals)        
        return res
