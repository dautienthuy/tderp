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

    @api.onchange("from_date")
    def compute_detail_list(self):
        self.load_detail_list()

    def load_detail_list(self):
        self.detail_ids = False
        if self.from_date:
            stagedone_id = self.env.ref('maintenance.stage_3').id
            stagecancel_id = self.env.ref('maintenance.stage_4').id
            detail_ids = []
            sql = '''
                SELECT
                    mr.code code
                    , CASE WHEN mr.maintenance_type = 'preventive' THEN 'Bảo hành' ELSE 'BTBD' END bhbt
                    , rp.name rp_name
                    , rp.phone
                    , rp.street
                    , mr.so_thang
                    , mr.backlog_note ghi_chu
                    , mr.number_maintenance so_lan
                    , mr.date_start ngay_bd
                    , mr.date_extend ngay_giahan
                    , mr.date_end ngay_kt
                    , '' du_kien
                    , to_char(request_date, 'MM-YYYY') AS ky
                    , '' sua_chua
                    , '' tem_kd
                FROM
                    maintenance_request mr
                LEFT JOIN
                    maintenance_equipment me ON mr.equipment_id = me.id
                LEFT JOIN
                    res_partner rp ON me.customer_id = rp.id
                WHERE
                    stage_id NOT IN (%(stagecancel_id)s)
                    AND request_date >= '%(date_from)s'
                    AND request_date <= '%(date_to)s'
                ''' % {
                'date_to': self.to_date,
                'date_from': self.from_date,
                'stagecancel_id': stagecancel_id,
            }
            self.env.cr.execute(sql)
            list_data = self.env.cr.dictfetchall()
            #
            for d in list_data:
                detail_ids.append((0, 0, {
                    'code': d['code'],
                    'bhbt': d['bhbt'],
                    'rp_name': d['rp_name'],
                    'phone': d['phone'],
                    'street': d['street'],
                    'so_thang': d['so_thang'],
                    'ghi_chu': d['ghi_chu'],
                    'so_lan': d['so_lan'],
                    'ngay_bd': d['ngay_bd'],
                    'ngay_giahan': d['ngay_giahan'],
                    'ngay_kt': d['ngay_kt'],
                    'du_kien': d['du_kien'],
                    'ky': d['ky'],
                    'sua_chua': d['sua_chua'],
                    'tem_kd': d['tem_kd']
                }))
            self.detail_ids = detail_ids


class WzTdReportMaintenanceDetail(models.TransientModel):
    _name = 'wz.td.report.maintenance.detail'
    _description = "Wz Td Report Maintenance Detail"

    report_id = fields.Many2one("wz.td.report.maintenance", ondelete="cascade")
    code = fields.Char("Mã BHBT")
    bhbt = fields.Char('BH/BT')
    rp_name = fields.Char("Khách hàng")
    phone = fields.Char('SĐT KH')
    street = fields.Char('Địa chỉ')
    so_thang = fields.Integer('Số thang')
    ghi_chu = fields.Text('Ghi chú')
    so_lan = fields.Integer('Số lần')
    ngay_bd = fields.Date('Ngày bắt đầu')
    ngay_giahan = fields.Date('Ngày gia hạn')
    ngay_kt = fields.Date('Ngày kết thúc')
    du_kien = fields.Char('Dự kiến')
    ky = fields.Char('Kỳ làm việc')
    sua_chua = fields.Char('Sửa chữa')
    tem_kd = fields.Char('Tem kiểm định')
    state = fields.Char('Trạng thái')