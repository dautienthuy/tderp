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


class WzTdReportWeeklyLine(models.Model):
    _name = 'wz.td.report.weekly.line'
    _description = "Wz Td Report Weekly Line"
    _auto = False
    _order = "date desc"
    _rec_name = "backlog_status"

    backlog_status = fields.Selection([
        ('01', 'Bảo hành'),
        ('02', 'Gia hạn bảo hành'),
        ('03', 'Bảo trì'),
        ('04', 'BT Free'),
        ('05', 'Dừng BH, BT'),
        ('06', 'Tạm dừng'),
        ('07', 'Thang mới'),
        ('08', 'Khác'),
    ], string=u"Nội dung")
    ton_dau = fields.Integer("Tồn đầu")
    du_kien = fields.Integer("Dự kiến")
    hoan_thanh_lich = fields.Integer("Hoàn thành theo lịch")
    ngoai_lich = fields.Integer("Ngoài lịch")
    ton_cuoi = fields.Integer("Tồn cuối")

    def init(self):
        vwName = self._table
        cr = self._cr
        tools.drop_view_if_exists(cr, vwName)
        cr.execute(
            """Create or replace view %s as
                Select
                    row_number() over (order by backlog_status) as id,
                    *
                from
                    (
                    Select
                        mr.backlog_status
                        , null ton_dau
                        , null du_kien
                        , null hoan_thanh_lich
                        , null ngoai_lich
                        , null ton_cuoi
                    from
                        maintenance_request mr
                    group by mr.backlog_status
                    ) vw
                order by backlog_status"""
            % vwName
        )
