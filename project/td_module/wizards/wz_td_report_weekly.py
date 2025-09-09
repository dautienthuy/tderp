# -*- encoding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools


class WzTdReportWeekly(models.TransientModel):
    _name = 'wz.td.report.weekly'
    _description = "Wz Td Report Weekly"
    _rec_name = "name"

    date_from = fields.Date(u'Từ ngày', required=True)
    date_to = fields.Date(u'Đến ngày', compute="_compute_date_to", store=True)
    name = fields.Char("Tuần", compute="_compute_name") # Ví dụ: Tuần 1 (01-08/08)
    week_in_month = fields.Integer("Tuần trong tháng", compute="_compute_week_in_month")
    detail_ids = fields.One2many("wz.td.report.weekly.line", "report_id", string="Báo cáo theo loại")

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

    @api.onchange("date_from")
    def compute_detail_list(self):
        self.load_detail_list()

    def load_detail_list(self):
        self.detail_ids = False
        if self.date_from:
            stagedone_id = self.env.ref('maintenance.stage_3').id
            stagecancel_id = self.env.ref('maintenance.stage_4').id
            detail_ids = []
            sql = '''
                SELECT
                    backlog_status
                    , SUM(CASE 
                        WHEN request_date < '%(date_from)s' AND stage_id NOT IN (%(stagedone_id)s, %(stagecancel_id)s)
                        THEN 1
                        ELSE 0
                    END) ton_dau
                    , SUM(CASE 
                        WHEN request_date <= '%(date_to)s' AND stage_id NOT IN (%(stagedone_id)s, %(stagecancel_id)s)
                        THEN 1
                        ELSE 0
                    END) ton_cuoi
                    , SUM(CASE 
                        WHEN request_date > '%(date_from)s' AND request_date <= '%(date_to)s' AND stage_id NOT IN (%(stagedone_id)s, %(stagecancel_id)s)
                        THEN 1
                        ELSE 0
                    END) du_kien
                    , SUM(CASE 
                        WHEN 
                            request_date > '%(date_from)s' AND 
                            request_date <= '%(date_to)s' AND 
                            stage_id IN (%(stagedone_id)s) AND
                            request_date <= date_end
                        THEN 1
                        ELSE 0
                    END) theo_lich
                    , SUM(CASE 
                        WHEN 
                            request_date > '%(date_from)s' AND 
                            request_date <= '%(date_to)s' AND 
                            stage_id IN (%(stagedone_id)s) AND
                            request_date > date_end
                        THEN 1
                        ELSE 0
                    END) ngoai_lich
                FROM
                    maintenance_request mr
                WHERE
                    -- mr.request_date >= '%(date_from)s'
                    -- AND mr.request_date <= '%(date_to)s'
                    stage_id NOT IN (%(stagecancel_id)s)
                GROUP BY
                    backlog_status;
                ''' % {
                'date_to': self.date_to,
                'date_from': self.date_from,
                'stagedone_id': stagedone_id,
                'stagecancel_id': stagecancel_id,
            }
            self.env.cr.execute(sql)
            print (sql)
            list_data = self.env.cr.dictfetchall()
            #
            for d in list_data:
                detail_ids.append((0, 0, {
                    'backlog_status': d['backlog_status'],
                    'ton_dau': d['ton_dau'],
                    'du_kien': d['du_kien'],
                    'theo_lich': d['theo_lich'],
                    'ngoai_lich': d['ngoai_lich'],
                    'ton_cuoi': d['ton_cuoi'],
                }))
            self.detail_ids = detail_ids


class WzTdReportWeeklyLine(models.TransientModel):
    _name = 'wz.td.report.weekly.line'
    _description = "Wz Td Report Weekly Line"

    report_id = fields.Many2one("wz.td.report.weekly", ondelete="cascade")
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
    theo_lich = fields.Integer("Theo lịch")
    ngoai_lich = fields.Integer("Ngoài lịch")
    ton_cuoi = fields.Integer("Tồn cuối")
