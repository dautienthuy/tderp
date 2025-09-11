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
    code = fields.Char("Mã BHBT")
    bhbt = fields.Char('BH/BT')
    rp_name = fields.Char("Khách hàng")
    phone = fields.Char('SĐT KH')
    street = fields.Char('Địa chỉ')
    so_thang = fields.Float('Số thang')
    ghi_chu = fields.Text('Ghi chú')
    so_lan = fields.Integer('Số lần')
    ngay_bd = fields.Date('Ngày bảo dưỡng')
    ngay_giahan = fields.Date('Ngày gia hạn')
    ngay_kt = fields.Date('Ngày kết thúc')
    du_kien = fields.Char('Dự kiến')
    ky = fields.Char('Kỳ làm việc')
    sua_chua = fields.Char('Sửa chữa')
    tem_kd = fields.Char('Tem kiểm định')
    state = fields.Char('Trạng thái')