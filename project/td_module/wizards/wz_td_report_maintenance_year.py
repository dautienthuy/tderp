# -*- encoding: utf-8 -*-

from odoo import api, fields, models


class WzTdReportMaintenanceYear(models.TransientModel):
    _name = 'wz.td.report.maintenance.year'
    _description = "Wz Td Report Maintenance Year"
    _rec_name = "from_date"

    from_date = fields.Date('Từ ngày')
    to_date = fields.Date('Đến ngày')
    maintenance_request_id = fields.Many2one('maintenance.request', 'Maintenance Request')
    detail_ids = fields.One2many("wz.td.report.maintenance.year.detail", "report_id", string="Chi tiết")


class WzTdReportMaintenanceYearDetail(models.TransientModel):
    _name = 'wz.td.report.maintenance.year.detail'
    _description = "Wz Td Report Maintenance Year Detail"

    report_id = fields.Many2one("wz.td.report.maintenance", ondelete="cascade")