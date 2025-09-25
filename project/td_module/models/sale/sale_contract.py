from odoo import models, fields, api, _


class SaleContract(models.Model):
    _name = "sale.contract"
    _description = "Sale Contract"

    order_id = fields.Many2one('sale.order', string="Báo giá")
    name = fields.Char(string="Tên hợp đồng")
    code = fields.Char(string="Mã nội bộ")
    number = fields.Char(string="Số hợp đồng", default='New', readonly=True, copy=False)
    partner_id = fields.Many2one("res.partner", string="Khách hàng", required=True)
    street = fields.Char(related='partner_id.street', string="Địa chỉ", readonly="1")
    date_order = fields.Datetime(string="Ngày tạo", default=fields.Datetime.now)
    date_contract = fields.Datetime(string="Ngày hợp đồng")
    user_id = fields.Many2one("res.users", string="Người tạo", default=lambda self: self.env.user)
    currency_id = fields.Many2one("res.currency", string="Tiền", required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    amount_total = fields.Monetary(string="Tổng", currency_field="currency_id")
    state = fields.Selection([
        ('draft', 'Chờ ký'),
        ('confirm', 'Đã ký'),
        ('cancel', 'Hủy'),
    ], string="Status", default='draft')

    contract_line_ids = fields.One2many("sale.contract.line", "contract_id", string="Chi tiết")
    sale_payment_term_ids = fields.One2many(comodel_name='sale.payment.term', inverse_name='contract_order_id')
    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.company)
    sale_type = fields.Selection(
        [
            ('bm', 'Bán mới'),
            ('sc', 'Sửa chữa'),
            ('bt', 'Bảo trì')
        ], string="Loại hợp đồng", default='bm')

    def action_set_draft(self):
        self.write({'state': 'draft'})

    def action_confirm(self):
        self.write({'state': 'confirm'})
    
    @api.model_create_multi
    def create(self, vals_list):
        base_self = self

        for vals in vals_list:
            company = vals.get('company_id') and base_self.env['res.company'].browse(
                vals['company_id']) or base_self.env.company

            default_names = {None, '/', _("New")}
            if vals.get('number') in default_names:
                qtype = vals.get('sale_type') or 'bm'
                code_map = {
                    'bt': 'sale.contract.bt',
                    'bm': 'sale.contract.bm',
                    'sc': 'sale.contract.sc',
                }
                seq_code = code_map.get(qtype, 'sale.contract.bm')

                seq_date = None
                if vals.get('create_date'):
                    seq_date = fields.Datetime.context_timestamp(
                        base_self.with_company(company),
                        fields.Datetime.to_datetime(vals['create_date'])
                    )

                vals['number'] = base_self.with_company(company).env['ir.sequence'].next_by_code(
                    seq_code, sequence_date=seq_date
                ) or _("New")

        return super(SaleContract, base_self).create(vals_list)

class SaleContractLine(models.Model):
    _name = "sale.contract.line"
    _description = "Contract Line"

    contract_id = fields.Many2one("sale.contract", string="Hợp đồng", ondelete="cascade")
    sale_order_line_id = fields.Many2one('sale.order.line', string="Source Sale Order Line")
    product_template_id = fields.Many2one(
        comodel_name='product.template',
        domain=[('sale_ok', '=', True)], string=u"Sản phẩm", required=True)
    name = fields.Text(string="Chi tiết", required=True)
    product_uom_qty = fields.Float(string="Số lượng", default=1.0)
    price_unit = fields.Float(string="Đơn giá")
    price_subtotal = fields.Monetary(string="Thành tiền", compute="_compute_subtotal", store=True)
    currency_id = fields.Many2one(related="contract_id.currency_id", store=True, readonly=True)

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.price_unit
