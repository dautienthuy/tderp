# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_date, formatLang, frozendict

from dateutil.relativedelta import relativedelta


class SalePlan(models.Model):
    _name = "sale.plan"
    _description = "Sale Plan"

    name = fields.Char(string=u'Nội dung')
    date = fields.Date(string=u'Ngày kế hoạch')
    order_id = fields.Many2one('sale.order', string=u'Đơn hàng')
    excurtion_progress_ids = fields.One2many(
        comodel_name='sale.excurtion.progress', inverse_name='sale_plan_id')
    construction_schedule_ids = fields.One2many(
        comodel_name='sale.construction.schedule', inverse_name='sale_plan_id')

class SaleExcurtionProgress(models.Model):
    _name = "sale.excurtion.progress"
    _description = "Sale Excurtion Progress"

    name = fields.Char(string=u'Nội dung')
    date = fields.Date(string=u'Ngày kế hoạch')
    sale_plan_id = fields.Many2one('sale.plan', string=u'kế hoạch')


class SaleConstructionSchedule(models.Model):
    _name = "sale.construction.schedule"
    _description = "Sale Construction Schedule"

    name = fields.Char(string=u'Nội dung')
    date = fields.Date(string=u'Ngày kế hoạch')
    sale_plan_id = fields.Many2one('sale.plan', string=u'kế hoạch')
