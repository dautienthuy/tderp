# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError, Warning, UserError
from datetime import timedelta
from datetime import date
from dateutil.relativedelta import relativedelta


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
    tem_kd = fields.Char(u'Tem kiểm định')
    date_actual  = fields.Date(string=u'Ngày thực tế')
    date_extend  = fields.Date(string=u'Ngày gia hạn')
    so_thang = fields.Integer('Số thang')
    maintenance_type = fields.Selection([
        ('corrective', 'BTBD'), 
        ('preventive', 'Bảo hành')], 
        string='Kiểu bảo trì', 
        default="corrective")
    date_done = fields.Date(string=u'Ngày hoàn thành')
    last_working_day = fields.Date(string=u'Ngày làm việc gần nhất')
    last_employee_id = fields.Many2one('hr.employee',  u'KTV gần nhất ')
    number_maintenance = fields.Integer(u'Số lần BT/BD')
    need_to_check = fields.Boolean('Cần kiểm tra')
    #
    backlog_status = fields.Selection([
        ('01', 'Bảo hành'),
        ('02', 'Gia hạn bảo hành'),
        ('03', 'Bảo trì'),
        ('04', 'BT Free'),
        ('05', 'Dừng BH, BT'),
        ('06', 'Tạm dừng'),
        ('07', 'Thang mới'),
        ('08', 'Khác'),
    ], string=u"Hạng mục", default='01')
    backlog_note = fields.Text("Ghi chú")
    #
    state = fields.Selection(
        selection=[
            ('draft', 'Mở'),
            ('open', 'Đang chạy'),
            ('paused', 'Tạm dừng'),
            ('close', 'Hoàn thành'),
            ('cancelled', 'Hủy')],
        string='Status',
        copy=False,
        default='draft')
    sale_plan_count = fields.Integer(compute='_compute_sale_plan_count', string=u"Số kế hoạch", store=True)
    sale_plan_ids = fields.One2many('sale.plan', 'equipment_id')
    sale_payment_term_ids = fields.One2many(comodel_name='sale.payment.term', inverse_name='equipment_id')

    @api.depends('sale_plan_ids')
    def _compute_sale_plan_count(self):
        for r in self:
            r.sale_plan_count = len(r.sale_plan_ids)

    def btn_sale_plan(self):
        sale_plan_exit =  self.env['sale.plan'].search([('order_id', '=', self.order_id.id)])
        if sale_plan_exit:
            sale_plan_exit.write({'equipment_id': self.id})
        # if not sale_plan_exit:
        #     vals = ({
        #         'equipment_id': self.id,
        #         'partner_id': self.customer_id.id})
        #     sale_plan = self.env['sale.plan'].create(vals)
        #     return sale_plan

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
            'company_id': self.company_id.id or self.env.company.id,
            'backlog_status': self.backlog_status,
            'so_thang': self.so_thang,
            'number_maintenance': self.number_maintenance,
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
                    'user_id': line.user_id.id,
                    'employee_id': self.employee_id.id,
                    'date_start': line.start_date,
                    'date_end': line.end_date,
                })
                maintenance_requests = self.env['maintenance.request'].create(vals)
                line.sudo().write({
                    'code_maintenance': maintenance_requests.code,
                    'maintenance_request_id': maintenance_requests.id})

    @api.model
    def schedule_info_maintenance_equipment_expire(self):
        today = fields.Date.today()
        fitler_date = today + relativedelta(day=10)
        sql = '''
            SELECT
                id
            FROM
                maintenance_equipment
            WHERE
                (need_to_check = 'f' OR need_to_check is null)
                AND state not in ('draft', 'close', 'cancelled')
                AND date_done <= '%s';
        ''' % fitler_date
        self._cr.execute(sql)
        print (sql)
        equipment_ids = [x[0] for x in self._cr.fetchall()]
        for r_id in equipment_ids:
            o_equipment = self.env['maintenance.equipment'].search([('id', 'in', r_id)])
            o_equipment.write({'need_to_check': True})
