# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class EquipmentPartsList(models.Model):
    _name = 'equipment.parts.list'    
    _description = 'Equipment Parts List'

    maintenance_equipment_id = fields.Many2one('maintenance.equipment', string=u'Equipment')
    code = fields.Char(u'Serial')    
    unit = fields.Selection([('chi', u'Chiếc'), ('cai', u'Cái')], string=u'Unit')
    quantity = fields.Float(u'Quantity')
    description = fields.Char(u'Description')
