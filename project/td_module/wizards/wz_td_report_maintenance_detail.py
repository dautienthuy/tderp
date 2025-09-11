# -*- encoding: utf-8 -*-

from odoo import api, fields, models


class WzTdReportMaintenance(models.TransientModel):
    _name = 'wz.td.report.maintenance'
    _description = "Wz Td Report Maintenance"
    _rec_name = "from_date"

    from_date = fields.Date('Từ ngày')
    to_date = fields.Date('Đến ngày')
    maintenance_request_id = fields.Many2one('maintenance.request', 'Maintenance Request')
    detail_ids = fields.One2many("wz.td.report.maintenance.detail", "report_id", string="Chi tiết")


class WzTdReportMaintenanceDetail(models.TransientModel):
    _name = 'wz.td.report.maintenance.detail'
    _description = "Wz Td Report Maintenance Detail"

    report_id = fields.Many2one("wz.td.report.maintenance", ondelete="cascade")
