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
    location_id = fields.Many2one('stock.location', "Location")
    payment_method = fields.Selection([
        ('c', 'Cash'),
        ('b', 'Bank'),
        ('o', 'Other'),
    ], string="Payment Method")
    sale_payment_term_ids = fields.One2many(comodel_name='sale.payment.term', inverse_name='order_id')
    client_code = fields.Char(u'Số hợp đồng')
    date_done = fields.Date(u'Ngày hoàn thành', copy=False)
    feature = fields.Text(u'Đặc tính')
    duration_contract = fields.Integer(u'Tiến độ hợp đồng')
    sale_plan_count = fields.Integer(compute='_compute_sale_plan_count', string=u"Số kế hoạch", store=True)
    sale_plan_ids = fields.One2many('sale.plan', 'order_id')

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
