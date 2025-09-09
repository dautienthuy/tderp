from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import date_utils, get_lang, html_escape

class MaintenanceTarget(models.Model):
    _name = "maintenance.target"
    _description = "Maintenance Target"

    def _default_year(self):
        today_date = fields.Date.context_today(self)
        return today_date.strftime('%Y')

    def _default_month(self):
        today_date = default_date = fields.Date.context_today(self)
        if today_date.day <= 10:
            default_date = fields.Date.context_today(self) - relativedelta.relativedelta(months=1)
        return default_date.strftime('%m')

    name = fields.Char("Tên", compute="_compute_name", store=True)
    month = fields.Selection([
        ("01", "Tháng 1"),
        ("02", "Tháng 2"),
        ("03", "Tháng 3"),
        ("04", "Tháng 4"),
        ("05", "Tháng 5"),
        ("06", "Tháng 6"),
        ("07", "Tháng 7"),
        ("08", "Tháng 8"),
        ("09", "Tháng 9"),
        ("10", "Tháng 10"),
        ("11", "Tháng 11"),
        ("12", "Tháng 12"),
        ], default=_default_month, string="Tháng")
    year = fields.Char(default=_default_year, string="Năm")
    from_date = fields.Date(
        string="Từ ngày", required="1")
    to_date = fields.Date(
        string="Đến ngày", required="1")
    line_ids = fields.One2many("maintenance.target.line", "monthly_id", string="Tuần")

    @api.onchange('month', 'year')
    def _compute_period_dates(self):
        for record in self:
            period_start = fields.Date.context_today(self).replace(day=1, month=int(record.month), year=int(record.year))
            this_month_start, this_month_end = date_utils.get_month(period_start)
            record.from_date = this_month_start
            record.to_date = this_month_end

    @api.depends("month", "year")
    def _compute_name(self):
        for rec in self:
            if rec.month and rec.year:
                month = rec.month
                year = rec.year
                rec.name = f"{month}/{year}"

class MaintenanceTargetLine(models.Model):
    _name = "maintenance.target.line"
    _description = "Maintenance Target Line"

    monthly_id = fields.Many2one("maintenance.target", ondelete="cascade")
    user_id = fields.Many2one("res.users", string="Nhân viên", required=True)
    working_day = fields.Float("Ngày làm việc")
    target_week1 = fields.Integer("Chỉ tiêu tuần 1")
    target_week2 = fields.Integer("Chỉ tiêu tuần 2")
    target_week3 = fields.Integer("Chỉ tiêu tuần 3")
    target_week4 = fields.Integer("Chỉ tiêu tuần 4")
    target_requests = fields.Integer("Chỉ tiêu xử lý", compute="_total_target", store=True)
    achieved_requests = fields.Integer("Đã xử lý", compute="_compute_achieved", store=True)
    progress = fields.Float("Tiến độ (%)", compute="_compute_progress", store=True)

    request_ids = fields.One2many("maintenance.request", "target_line_id", string="Yêu cầu bảo trì")

    @api.depends("target_week1","target_week2","target_week3",'target_week4')
    def _total_target(self):
        for rec in self:
            rec.target_requests = rec.target_week1 + rec.target_week2 + rec.target_week3 + rec.target_week4

    @api.depends("request_ids")
    def _compute_achieved(self):
        for rec in self:
            done_reqs = rec.request_ids.filtered(lambda r: r.stage_id.name == "Done")
            rec.achieved_requests = len(done_reqs)

    @api.depends("achieved_requests", "target_requests")
    def _compute_progress(self):
        for rec in self:
            rec.progress = 0
            if rec.target_requests:
                rec.progress = 100.0 * rec.achieved_requests / rec.target_requests
