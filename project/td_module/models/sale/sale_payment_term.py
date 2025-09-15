# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_date, formatLang, frozendict

from dateutil.relativedelta import relativedelta


class SalePaymentTerm(models.Model):
    _name = "sale.payment.term"
    _description = "Payment Terms"
    _order = "sequence, id"

    name = fields.Char(string=u'Điều khoản thanh toán', required=True)
    type = fields.Selection([('adv', u'Tạm ứng'),('progress', u'Thanh toán'),('retention', u'Giữ lại')], required=True)
    payment_type = fields.Selection([('b', u'Ngân hàng'),('c', u'Tiền mặt'),('o', u'Khác')])
    account_bank = fields.Char(u'Số tài khoản')
    bank = fields.Char(u'Ngân hàng')
    ghi_chu = fields.Char(u'Ghi chú')
    note = fields.Html(string=u'Mô tả')
    sequence = fields.Integer(required=True, string=u'Thứ tự')
    start_date = fields.Date(string=u'Ngày bắt đầu')
    end_date = fields.Date(string=u'Ngày kết thúc')
    total_amount = fields.Float(string=u'Số tiền được tính', compute='_compute_amount', copy=False, store=True)
    epui_total_amount = fields.Float(string=u'Số tiền')
    percent_payment = fields.Float(string=u'Tỉ lệ(%)')
    total_paid = fields.Float(string=u'Thanh toán')
    order_id = fields.Many2one('sale.order', string=u'Sale Order')
    equipment_id = fields.Many2one('maintenance.equipment', string=u'Trang thiết bị')

    @api.depends('percent_payment', 'order_id.amount_total', 'epui_total_amount')
    def _compute_amount(self):
        for line in self:
            if line.order_id:
                line.total_amount = line.order_id.amount_total * line.percent_payment*0.01
            elif not line.order_id:
                line.total_amount = line.epui_total_amount
