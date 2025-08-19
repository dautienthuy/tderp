# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_date, formatLang, frozendict

from dateutil.relativedelta import relativedelta


class SalePlan(models.Model):
    _name = "sale.plan"
    _description = "Sale Plan"

    name = fields.Char(string=u'Điều khoản thanh toán', required=True)
    date = fields.Date(string=u'Ngày kế hoạch')
    order_id = fields.Many2one('sale.order', string=u'Đơn hàng')


class SaleExcurtionProgress(models.Model):
    _name = "sale.excurtion.progress"
    _description = "Sale Excurtion Progress"

    name = fields.Char(string=u'Tên', required=True)
    date = fields.Date(string=u'Ngày kế hoạch')
    sale_plan_id = fields.Many2one('sale.plan', string=u'kế hoạch')


class SaleConstructionSchedule(models.Model):
    _name = "sale.construction.schedule"
    _description = "Sale Construction Schedule"

    name = fields.Char(string=u'Tên', required=True)
    date = fields.Date(string=u'Ngày kế hoạch')
    sale_plan_id = fields.Many2one('sale.plan', string=u'kế hoạch')
