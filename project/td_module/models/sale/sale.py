# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_address = fields.Text(u'Delivery Address')
    inv_address = fields.Text(u'Invoice Address')
    location_id = fields.Many2one('stock.location', "Location")
    payment_method = fields.Selection([
        ('c', 'Cash'),
        ('b', 'Bank'),
        ('o', 'Other'),
    ], string="Payment Method")
