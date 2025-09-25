# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_partner_domain(self):
        sql = """
            SELECT
                partner_id
            FROM res_users
        """
        self.env.cr.execute(sql)
        ids = [f[0] for f in self.env.cr.fetchall()]
        return "[ ('id', 'not in', %s)]" %ids

    partner_id = fields.Many2one(domain=lambda self: self._get_partner_domain())
    street = fields.Char(related='partner_id.street', string="Địa chỉ")
    location_id = fields.Many2one('stock.location', "Location")
    payment_method = fields.Selection([
        ('c', 'Cash'),
        ('b', 'Bank'),
        ('o', 'Other'),
    ], string="Payment Method")
    sale_payment_term_ids = fields.One2many(comodel_name='sale.payment.term', inverse_name='order_id')
    client_code = fields.Char(u'Số hợp đồng')
    date_done = fields.Date(u'Ngày hoàn thành', copy=False)
    order_create_date = fields.Date(u'Ngày tạo', copy=False)
    feature = fields.Text(u'Đặc tính')
    duration_contract = fields.Integer(u'Tiến độ hợp đồng')
    sale_plan_count = fields.Integer(compute='_compute_sale_plan_count', string=u"Số kế hoạch", store=True)
    sale_plan_ids = fields.One2many('sale.plan', 'order_id')
    sale_type = fields.Selection(
        [
            ('bm', 'Bán mới'),
            ('sc', 'Sửa chữa'),
            ('bt', 'Bảo trì')
        ], string="Loại báo giá", default='bm')
    other_name = fields.Char(u'Tên hợp đồng')
    maintenance_equip_count = fields.Integer(compute='_compute_maintenance_equip_count', string=u"Số dự án", store=True)
    maintenance_equip_ids = fields.One2many('maintenance.equipment', 'order_id')
    image_attachment_ids = fields.Many2many(
        'ir.attachment', string="Image",
        domain=[('mimetype', 'ilike', 'image/')]
    )

    # @api.constrains('client_code')
    # def _check_code(self):
    #     check = self.search_count([('client_code', '=', self.client_code)])
    #     if check > 1 :
    #         raise UserError(_('Số hợp đồng  %s đã có sãn trên hệ thống.' % self.client_code))

    @api.depends('sale_plan_ids')
    def _compute_sale_plan_count(self):
        for so in self:
            so.sale_plan_count = len(so.sale_plan_ids)

    def btn_sale_plan(self):
        sale_plan_exit =  self.env['sale.plan'].search([('order_id', '=', self.id)])
        if not sale_plan_exit:
            vals = ({
                'order_id': self.id,
                'partner_id':self.partner_id.id})
            sale_plan = self.env['sale.plan'].create(vals)
            return sale_plan

    @api.depends('maintenance_equip_ids')
    def _compute_maintenance_equip_count(self):
        for so in self:
            so.maintenance_equip_count = len(so.maintenance_equip_ids)

    def _td_prepare_maintenance_equip_vals(self):
        self.ensure_one()
        return {
            'name':  _('[%s] %s') % (self.client_code, self.other_name),
            'order_id': self.id,
            'customer_id': self.partner_id.id
        }

    def btn_generate_requests(self):
        requests = self.env['maintenance.equipment'].search([('state', '!=', 'cancelled'),
                                                    ('order_id', '=', self.id)])
        if not requests:
            vals = self._td_prepare_maintenance_equip_vals()
            maintenance_requests = self.env['maintenance.equipment'].create(vals)

    def action_confirm(self):
        res = super().action_confirm()
        #self.btn_generate_requests()
        return res

    def get_lines_values(self):
        self.ensure_one()
        lines_values = []
        for line in self.order_line:
            lines_values.append({
                "product_template_id": line.product_template_id.id,
                "name": line.name,
                "product_uom_qty": line.product_uom_qty,
                "price_unit": line.price_unit,
                "sale_order_line_id": line.id
            })
        return lines_values

    def get_payment_term_values(self):
        self.ensure_one()
        lines_values = []
        for line in self.sale_payment_term_ids:
            lines_values.append({
                "type": line.type,
                "start_date": line.start_date,
                "end_date": line.end_date,
                "sequence": line.sequence,
                "name": line.name,
                "percent_payment": line.percent_payment,
                "total_amount": line.total_amount,
                "total_paid": line.total_paid,
                "date": line.date,
                "payment_type": line.payment_type,
                "account_bank": line.account_bank,
                "bank": line.bank,
                "bank": line.ghi_chu
            })
        return lines_values

    def btn_create_contract(self):
        requests = self.env['sale.contract'].search([('state', '!=', 'cancel'),
                                                    ('order_id', '=', self.id)])
        if not requests:
            vals = {
                'order_id': self.id,
                'sale_type': self.sale_type,
                'name': self.other_name,
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
                'contract_line_ids': [(0, 0, value) for value in self.get_lines_values()],
                'sale_payment_term_ids': [(0, 0, value) for value in self.get_payment_term_values()],
            }
            sale_contract = self.env['sale.contract'].create(vals)
            self.sale_plan_ids.write({'contract_id': sale_contract.id})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.contract',
                'res_id': sale_contract.id,
                'view_ids': [(False, 'form')],
                'view_mode': 'form',
            }

    @api.model_create_multi
    def create(self, vals_list):
        base_self = self

        for vals in vals_list:
            company = vals.get('company_id') and base_self.env['res.company'].browse(
                vals['company_id']) or base_self.env.company

            default_names = {None, '/', _("New")}
            if vals.get('name') in default_names:
                qtype = vals.get('sale_type') or 'bm'
                code_map = {
                    'bt': 'sale.order.bt',  # Bảo trì → BGBTxxxxx
                    'bm': 'sale.order.bm',  # Bán mới → BGBMxxxxx
                    'sc': 'sale.order.sc',  # Sửa chữa → xxxMM.YY/BGSC
                }
                seq_code = code_map.get(qtype, 'sale.order.bm')

                seq_date = None
                if vals.get('date_order'):
                    seq_date = fields.Datetime.context_timestamp(
                        base_self.with_company(company),
                        fields.Datetime.to_datetime(vals['date_order'])
                    )

                vals['name'] = base_self.with_company(company).env['ir.sequence'].next_by_code(
                    seq_code, sequence_date=seq_date
                ) or _("New")

        return super(SaleOrder, base_self).create(vals_list)
