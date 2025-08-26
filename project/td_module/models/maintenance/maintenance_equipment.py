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
    customer_id = fields.Many2one('res.partner', u'Khách hàng')
    street = fields.Char(related='customer_id.street', string="Địa chỉ")
    phone = fields.Char(related='customer_id.phone', string="Số điện thoại")
    #
    maintenance_type = fields.Selection([
        ('corrective', 'Bảo trì'), 
        ('preventive', 'Bảo dưỡng')], 
        string='Maintenance Type', 
        default="corrective")
    last_working_day = fields.Date(string=u'Ngày làm việc gần nhất')
    last_employee_id = fields.Many2one('hr.employee',  u'KTV gần nhất ')
    number_maintenance = fields.Integer(u'Số lần BT/BD')
    #
    backlog_status = fields.Selection([
        ('waiting_repair', 'Chờ sửa chữa'),
        ('waiting_disposal', 'Chờ thanh lý'),
        ('waiting_allocate', 'Chờ cấp phát'),
        ('waiting_purchase', 'Chờ mua sắm'),
    ], string="Tồn đọng", default=False)
    backlog_note = fields.Text("Ghi chú tồn đọng")
    #
    state = fields.Selection(
        selection=[('model', 'Model'),
            ('draft', 'Mở'),
            ('open', 'Đang chạy'),
            ('paused', 'Tạm dừng'),
            ('close', 'Hoàn thành'),
            ('cancelled', 'Hủy')],
        string='Status',
        copy=False,
        default='draft')

    def action_set_draft(self):
        self.write({'state': 'draft'})

    def action_confirm(self):
        self.write({'state': 'open'})

    def action_set_done(self):
        """ Close Registration """
        self.write({'state': 'close'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_pause(self):
        self.write({'state': 'paused'})

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
