# -*- encoding: utf-8 -*-

from odoo import api, fields, models


class WzTdReportSale(models.TransientModel):
    _name = 'wz.td.report.sale'
    _inherit = 'wz.td.report.base'
    _description = "Wz Td Report Sale"
    _report_name = 'td_module.sale_report_py3o'

    from_date = fields.Date('Từ ngày')
    to_date = fields.Date('Đến ngày')
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    type = fields.Selection([('pdf', 'Pdf'), ('excel', 'Excel')], string=u'Kiểu in', default='pdf')
