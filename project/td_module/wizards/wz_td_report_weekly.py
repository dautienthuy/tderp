# -*- encoding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools


class WzTdReportWeekly(models.TransientModel):
    _name = 'wz.td.report.weekly'
    _description = "Wz Td Report Weekly"
    _rec_name = "name"

    date_from = fields.Date(u'Từ ngày', required=True)
    date_to = fields.Date(u'Đến ngày', compute="_compute_date_to")
    name = fields.Char("Tuần", compute="_compute_name") # Ví dụ: Tuần 1 (01-08/08)
    week_in_month = fields.Integer("Tuần trong tháng", compute="_compute_week_in_month")

    @api.depends("date_from")
    def _compute_date_to(self):
        for rec in self:
            if rec.date_from:
                rec.date_to = rec.date_from + relativedelta(weeks=1)

    @api.depends("date_from")
    def _compute_week_in_month(self):
        for rec in self:
            if rec.date_from:
                rec.week_in_month = (rec.date_from.day - 1) // 7 + 1
            else:
                rec.week_in_month = False

    @api.depends("week_in_month", "date_from", "date_to")
    def _compute_name(self):
        for rec in self:
            if rec.week_in_month and rec.date_from and rec.date_to:
                rec.name = f"Tuần {rec.week_in_month} tháng {rec.date_from.strftime('%m/%Y')} " \
                           f"({rec.date_from.strftime('%d/%m')} - {rec.date_to.strftime('%d/%m')})"
            elif rec.date_from and rec.date_to:
                rec.name = f"{rec.date_from.strftime('%d/%m')} - {rec.date_to.strftime('%d/%m')}"
            else:
                rec.name = "Báo cáo tuần"

    def compute(self):
        return {"tag": "reload", "type": "ir.actions.act_window_close"}


