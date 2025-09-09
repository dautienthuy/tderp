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
