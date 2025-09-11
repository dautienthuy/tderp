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

    report_id = fields.Many2one("wz.td.report.maintenance.year", ondelete="cascade")
    bhbt = fields.Char('BH/BT')
    rp_name = fields.Char("Khách hàng")
    phone = fields.Char('SĐT KH')
    street = fields.Char('Địa chỉ')
    so_thang = fields.Float('Số thang')
    loai_thang = fields.Char('Loại thang')
    so_lan = fields.Integer('Số lần')
    ngay_bd = fields.Date('Ngày bắt đầu')
    ngay_kt = fields.Date('Ngày kết thúc')
    t1 = fields.Text('Tháng 1')
    t2 = fields.Text('Tháng 2')
    t3 = fields.Text('Tháng 3')
    t4 = fields.Text('Tháng 4')
    t5 = fields.Text('Tháng 5')
    t6 = fields.Text('Tháng 6')
    t7 = fields.Text('Tháng 7')
    t8 = fields.Text('Tháng 8')
    t9 = fields.Text('Tháng 9')
    t10 = fields.Text('Tháng 10')
    t11 = fields.Text('Tháng 11')
    t12 = fields.Text('Tháng 12')
