# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class MaintenanceChecklist(models.Model):
    _name = 'maintenance.checklist'    
    _description = 'Maintenance Checklist'

    code = fields.Char(u'Code')  
    name = fields.Char(u'Name')  
    description = fields.Char(u'Description')
