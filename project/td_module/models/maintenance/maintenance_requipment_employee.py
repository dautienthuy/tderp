# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class MaintenanceRequipmentEmployee(models.Model):
    _name = 'maintenance.requipment.employee'    
    _description = 'Maintenance Equipment Employee'

    equipment_id = fields.Many2one('maintenance.equipment', string=u'Vật tư thay thế')
    start_date = fields.Date(string=u'Ngày bắt đầu')
    end_date = fields.Date(string=u'Ngày kết thúc')
    delivery_date = fields.Date(string=u'Ngày giao hàng') 
    employee_id = fields.Many2one('hr.employee',  u'Kỹ thuật viên')
