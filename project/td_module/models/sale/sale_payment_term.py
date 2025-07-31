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
    note = fields.Html(string=u'Mô tả')
    sequence = fields.Integer(required=True, string=u'Thứ tự')
    start_date = fields.Date(string=u'Ngày bắt đầu')
    end_date = fields.Date(string=u'Ngày kết thúc')
    total_amount = fields.Float(string=u'Tổng tiền')
    percent_payment = fields.Float(string=u'Tỉ lệ(%)')
    order_id = fields.Many2one('sale.order', string=u'Sale Order')
