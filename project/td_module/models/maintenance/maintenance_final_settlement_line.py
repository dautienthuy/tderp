# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class MaintenanceFinalSettlementLine(models.Model):
    _name = 'maintenance.final.settlement.line'    
    _description = 'Maintenance Final Settlement Line'

    maintenance_request_id = fields.Many2one('maintenance.request', string=u'Maintenance')
    task_detail = fields.Text(u'Nội dung công việc')    
    uom_id = fields.Many2one('uom.uom', u'Đơn vị tính')
    task_qty = fields.Float(u'Số lượng công việc')
