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
    emp_ids = fields.One2many("wz.td.report.weekly.emp", "report_id", string="Báo cáo theo nhân viên")

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

    @api.onchange("date_from")
    def compute_detail_list(self):
        self.load_detail_list()
        self.load_emp_list()

    def load_emp_list(self):
        self.emp_ids = False
        if self.date_from:
            emp_ids = []
            stagedone_id = self.env.ref('maintenance.stage_3').id
            stagecancel_id = self.env.ref('maintenance.stage_4').id
            sql = '''
                SELECT
                    mr.user_id
                    , rp.name user_name
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
                    , SUM(CASE WHEN '%(date_from)s' >= mt.from_date AND '%(date_to)s' <= mt.to_date THEN mtl.working_day ELSE 0 END) ngay_lv
                    , SUM(CASE 
                        WHEN '%(date_from)s' >= mt.from_date AND '%(date_to)s' <= mt.to_date AND 1 = %(week_in_month)s THEN mtl.target_week1
                        WHEN '%(date_from)s' >= mt.from_date AND '%(date_to)s' <= mt.to_date AND 2 = %(week_in_month)s THEN mtl.target_week2
                        WHEN '%(date_from)s' >= mt.from_date AND '%(date_to)s' <= mt.to_date AND 3 = %(week_in_month)s THEN mtl.target_week3
                        WHEN '%(date_from)s' >= mt.from_date AND '%(date_to)s' <= mt.to_date AND 4 = %(week_in_month)s THEN mtl.target_week4
                        ELSE 0
                    END) chi_tieu_thang
                FROM
                    maintenance_request mr
                LEFT JOIN
                    maintenance_target_line mtl ON mr.target_line_id = mtl.id
                LEFT JOIN
                    maintenance_target mt ON mt.id = mtl.monthly_id
                LEFT JOIN
                    res_users ru ON mr.user_id = ru.id
                LEFT JOIN
                    res_partner rp ON ru.partner_id = rp.id
                WHERE
                    stage_id NOT IN (%(stagecancel_id)s)
                GROUP BY
                    mr.user_id, rp.name;
                '''% {
                'date_to': self.date_to,
                'date_from': self.date_from,
                'stagedone_id': stagedone_id,
                'stagecancel_id': stagecancel_id,
                'week_in_month': self.week_in_month
            }
            self.env.cr.execute(sql)
            list_data = self.env.cr.dictfetchall()
            #
            for d in list_data:
                emp_ids.append((0, 0, {
                    'user_id': d['user_id'],
                    'user_name': d['user_name'],
                    'ton_dau': d['ton_dau'],
                    'du_kien': d['du_kien'],
                    'theo_lich': d['theo_lich'],
                    'ngoai_lich': d['ngoai_lich'],
                    'ton_cuoi': d['ton_cuoi'],
                    'ngay_lv': d['ngay_lv'],
                    'chi_tieu_thang': d['chi_tieu_thang'],
                }))
            self.emp_ids = emp_ids

    def load_detail_list(self):
        self.detail_ids = False
        if self.date_from:
            stagedone_id = self.env.ref('maintenance.stage_3').id
            stagecancel_id = self.env.ref('maintenance.stage_4').id
            detail_ids = []
            sql = '''
                SELECT
                    backlog_status
                    , CASE 
                        WHEN backlog_status = '01' THEN 'Bảo hành'
                        WHEN backlog_status = '02' THEN 'Gia hạn bảo hành'
                        WHEN backlog_status = '03' THEN 'Bảo trì'
                        WHEN backlog_status = '04' THEN 'BT Free'
                        WHEN backlog_status = '05' THEN 'Dừng BH, BT'
                        WHEN backlog_status = '06' THEN 'Tạm dừng'
                        WHEN backlog_status = '07' THEN 'Thang mới'
                        WHEN backlog_status = '08' THEN 'Khác'
                    ELSE ''
                    END name_backlog_status
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
            list_data = self.env.cr.dictfetchall()
            #
            for d in list_data:
                detail_ids.append((0, 0, {
                    'backlog_status': d['backlog_status'],
                    'name_backlog_status': d['name_backlog_status'],
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
    name_backlog_status = fields.Char()
    ton_dau = fields.Integer("Tồn đầu")
    du_kien = fields.Integer("Dự kiến")
    theo_lich = fields.Integer("Theo lịch")
    ngoai_lich = fields.Integer("Ngoài lịch")
    ton_cuoi = fields.Integer("Tồn cuối")


class WzTdReportWeeklyEmp(models.TransientModel):
    _name = 'wz.td.report.weekly.emp'
    _description = "Wz Td Report Weekly Emp"

    report_id = fields.Many2one("wz.td.report.weekly", ondelete="cascade")
    user_id = fields.Many2one("res.users", string="Nhân viên", required=True)
    user_name = fields.Char()
    ngay_lv = fields.Integer(string="Ngày LV", default=0)
    chi_tieu_thang = fields.Integer(string="Chỉ tiêu thang", default=0)
    ton_dau = fields.Integer(string="Tồn Đầu", default=0)
    du_kien = fields.Integer(string="Dự kiến", default=0)
    theo_lich = fields.Integer(string="Theo lịch", default=0)
    ngoai_lich = fields.Integer(string="Ngoài lịch", default=0)
    ton_cuoi = fields.Integer(string="Tồn", default=0)
    note = fields.Text(string="Ghi chú")
