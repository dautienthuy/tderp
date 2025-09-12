# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class MaintenanceDetail(models.Model):
    _name = 'maintenance.detail'
    _description = 'Maintenance Detail'

    maintenance_request_id = fields.Many2one('maintenance.request', string=u'Maintenance')
    product_id = fields.Many2one('product.product', string='Mã hàng')
    technical_spec = fields.Char(string=u'Thông số kỹ thuật')
    uom_id = fields.Many2one('uom.uom', 'Đơn vị')
    quantity = fields.Float(u'Số lượng')
    unit_price = fields.Float(u'Đơn giá')
    amount = fields.Float(u'Thành tiền', compute='_compute_amount', store=True)
    note = fields.Char(u'Ghi chú')

    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.unit_price
