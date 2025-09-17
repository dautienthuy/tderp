# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_date, formatLang, frozendict

from dateutil.relativedelta import relativedelta
from datetime import timedelta


class SalePlan(models.Model):
    _name = "sale.plan"
    _description = "Sale Plan"

    name = fields.Char(string=u'Nội dung')
    date = fields.Date(string=u'Ngày kế hoạch')
    partner_id = fields.Many2one('res.partner', u'Khách hàng')
    street = fields.Char(related='partner_id.street', string="Địa chỉ")
    order_id = fields.Many2one('sale.order', string=u'Đơn hàng')
    equipment_id = fields.Many2one('maintenance.equipment', string=u'Trang thiết bị')
    excurtion_progress_ids = fields.One2many(
        comodel_name='sale.excurtion.progress', inverse_name='sale_plan_id')
    construction_schedule_ids = fields.One2many(
        comodel_name='sale.construction.schedule', inverse_name='sale_plan_id')
    #
    state = fields.Selection(
        selection=[
            ('draft', 'Mở'),
            ('open', 'Đang chạy'),
            ('close', 'Hoàn thành')],
        string='Status',
        copy=False,
        default='draft')

    def action_set_draft(self):
        self.write({'state': 'draft'})

    def action_confirm(self):
        self.write({'state': 'open'})

    def action_set_done(self):
        self.write({'state': 'close'})


class SaleExcurtionProgress(models.Model):
    _name = "sale.excurtion.progress"
    _description = "Sale Excurtion Progress"

    name = fields.Char(string=u'Nội dung')
    date = fields.Date(string=u'Ngày kế hoạch')
    sale_plan_id = fields.Many2one('sale.plan', string=u'kế hoạch')
    date_number = fields.Integer('Thời hạn')
    date_expected = fields.Date(string=u'Ngày dự kiến')
    note = fields.Char(string=u'Ghi chú')

    @api.onchange('date', 'date_number')
    def _onchange_date_expected(self):
        if self.date:
            self.date_expected = self.date + timedelta(self.date_number)


class SaleConstructionSchedule(models.Model):
    _name = "sale.construction.schedule"
    _description = "Sale Construction Schedule"

    name = fields.Char(string=u'Nội dung')
    date = fields.Date(string=u'Ngày kế hoạch')
    sale_plan_id = fields.Many2one('sale.plan', string=u'kế hoạch')
