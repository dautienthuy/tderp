# -*- encoding: utf-8 -*-

from odoo import api, fields, models


class WzTdReportMaintenanceDetail(models.TransientModel):
    _name = 'wz.td.report.maintenance.detail'
    _inherit = 'wz.td.report.base'
    _description = "Wz Td Report Maintenance Detail"
    _report_name = 'td_module.maintenance_detail_report_py3o'

    # @api.multi
    # def _get_contract_history(self):
    #     self.ensure_one()
    #     cr = self._cr
    #     fromDate = self.from_date
    #     toDate = self.to_date
    #     sql = """select 
    #                 id
    #             from 
    #                 kderp_contract_history 
    #             where 
    #                 date between '%s' and '%s'""" % (fromDate, toDate)
    #     cr.execute(sql)
    #     ch_ids = [id[0] for id in cr.fetchall()]
    #     self.detail_ids = ch_ids

    from_date = fields.Date('Từ ngày')
    to_date = fields.Date('Đến ngày')
    maintenance_request_id = fields.Many2one('maintenance.request', 'Maintenance Request')
    # detail_ids = fields.One2many(
    #     "kderp.contract.history", compute="_get_contract_history", string="Details")