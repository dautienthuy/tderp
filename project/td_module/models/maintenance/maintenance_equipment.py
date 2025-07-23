# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class MaintenanceEquipment(models.Model):
    _name = 'maintenance.equipment'
    _inherit = 'maintenance.equipment'
    _description = 'Maintenance Equipment'

    parent_equipment_id = fields.Many2one('maintenance.equipment', string='Parent Equipment')
    equipment_assign_to = fields.Selection(
        [('department', 'Department'), ('customer', 'Customer'), ('other', 'Other')],
        string='Used By',
        required=True,
        default='customer')
