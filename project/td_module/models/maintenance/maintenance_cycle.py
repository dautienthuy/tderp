# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class MaintenanceCycle(models.Model):
    _name = 'maintenance.cycle'    
    _description = 'Maintenance Cycle'

    maintenance_equipment_id = fields.Many2one('maintenance.equipment', string='Maintenance Equipment')
    maintenance_checklist_id = fields.Many2one('maintenance.checklist', string='Maintenance Checklist')
    date = fields.Date(string='Date')
    uom_id = fields.Many2one('uom.uom', 'Unit')
    warning_equipment = fields.Boolean(string=u'Warning')
    description = fields.Char(u'Description')
