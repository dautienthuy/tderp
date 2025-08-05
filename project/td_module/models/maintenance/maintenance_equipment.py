# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class MaintenanceEquipment(models.Model):
    _name = 'maintenance.equipment'
    _inherit = 'maintenance.equipment'
    _description = 'Maintenance Equipment'

    parent_equipment_id = fields.Many2one('maintenance.equipment', string='Parent Equipment')
    equipment_parts_list = fields.One2many('equipment.parts.list', 'maintenance_equipment_id', string=u'Equipment Parts List')
    maintenance_cycle_ids = fields.One2many('maintenance.cycle', 'maintenance_equipment_id', string=u'Maintenance Cycle')
    order_id = fields.Many2one('sale.order', string=u'Sale Order')
    expiry_inspection_stamp = fields.Text(u'Hạn tem kiểm định')
