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
    delivery_address = fields.Text(u'Delivery Address')
    inv_address = fields.Text(u'Invoice Address')
    location_id = fields.Many2one('stock.location', "Location")
    payment_method = fields.Selection([
        ('c', 'Cash'),
        ('b', 'Bank'),
        ('o', 'Other'),
    ], string="Payment Method")
    sale_payment_term_ids = fields.One2many(comodel_name='sale.payment.term', inverse_name='order_id')
    client_code = fields.Char(u'Số hợp đồng')
    date_done = fields.Datetime(u'Ngày hoàn thành', copy=False)
