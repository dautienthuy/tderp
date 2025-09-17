# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    detail = fields.Text(u"Thông số chi tiết")
