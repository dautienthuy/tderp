# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError, Warning, UserError


class MaintenanceEquipment(models.Model):
    _name = 'maintenance.equipment'
    _inherit = 'maintenance.equipment'
    _description = 'Maintenance Equipment'

    code = fields.Char(u'Mã nội bộ')
    parent_equipment_id = fields.Many2one('maintenance.equipment', string='Thiết bị gốc')
    equipment_parts_list = fields.One2many('equipment.parts.list', 'maintenance_equipment_id', string=u'Equipment Parts List')
    maintenance_cycle_ids = fields.One2many('maintenance.cycle', 'maintenance_equipment_id', string=u'Maintenance Cycle')
    order_id = fields.Many2one('sale.order', string=u'Đơn hàng')
    expiry_inspection_stamp = fields.Text(u'Hạn tem kiểm định')
    mainten_requipment_employee_ids = fields.One2many('maintenance.requipment.employee', 'equipment_id', string=u'Mainten. Mequipment Employee')

    @api.model_create_multi
    def create(self, vals_list):
        # We generate a standard reference
        for vals in vals_list:
            vals['code'] = self.env['ir.sequence'].next_by_code('maintenance.equipment') or '/'
        return super().create(vals_list)

    def _td_prepare_maintenance_request_vals(self, date):
        self.ensure_one()
        return {
            'name': _('Preventive Maintenance - %s', self.name),
            'request_date': date,
            'schedule_date': date,
            'category_id': self.category_id.id,
            'equipment_id': self.id,
            'maintenance_type': 'preventive',
            'owner_user_id': self.owner_user_id.id,
            'user_id': self.technician_user_id.id,
            'maintenance_team_id': self.maintenance_team_id.id,
            'duration': self.maintenance_duration,
            'company_id': self.company_id.id or self.env.company.id
        }

    def btn_generate_requests(self):
        """
            Generates maintenance request on the delivery_date or today if none exists
        """
        for line in self.mainten_requipment_employee_ids:
            requests = self.env['maintenance.request'].search([('stage_id.done', '=', False),
                                                    ('equipment_id', '=', self.id),
                                                    ('request_date', '=', line.delivery_date)])
            if not requests:
                if not line.delivery_date or not line.start_date or not line.end_date:
                    raise ValidationError(u'Thiếu thông tin ngày trong nhân sự thực hiện bảo trì')
                vals = self._prepare_maintenance_request_vals(line.delivery_date)
                vals.update({
                    'employee_id': line.employee_id.id,
                    'date_start': line.start_date,
                    'date_end': line.end_date,
                })
                maintenance_requests = self.env['maintenance.request'].create(vals)
