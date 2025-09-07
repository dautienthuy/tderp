# -*- encoding: utf-8 -*-

from odoo import api, fields, models, tools


class WzTdReportSale(models.TransientModel):
    _name = 'wz.td.report.sale'
    _description = "Wz Td Report Sale"
    _rec_name = "date_from"

    date_from = fields.Date('Từ ngày')
    date_to = fields.Date('Đến ngày')
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    detail_ids = fields.One2many("wz.td.report.sale.detail", compute="_get_detail_list", string="Details")

    def compute(self):
        return {"tag": "reload", "type": "ir.actions.act_window_close"}

    def _get_detail_list(self):
        cr = self._cr
        for obj in self.filtered(lambda obj: obj.date_from and obj.date_to):
            date_from = obj.date_from
            date_to = obj.date_to
            sqlCommand = """Select
                            distinct
                            tdsd.id,
                            code,
                            date
                        from
                            wz_td_report_sale_detail tdsd
                        where
                            date between '{date_from}' and '{date_to}'
                        order by
                            date
                            """.format(
                date_from=date_from, date_to=date_to
            )
            cr.execute(sqlCommand)
            data = cr.fetchall()
            if not data:
                obj.detail_ids = [(5, 0, 0)]
            else:
                obj.detail_ids = [x[0] for x in data]


class WzTdReportSaleDetail(models.Model):
    _name = 'wz.td.report.sale.detail'
    _description = "Wz Td Report Sale Detail"
    _auto = False
    _order = "date desc"
    _rec_name = "code"

    code = fields.Char("Số HĐ")
    date = fields.Date("Ngày")

    def init(self):
        vwName = self._table
        cr = self._cr
        tools.drop_view_if_exists(cr, vwName)
        cr.execute(
            """Create or replace view %s as
                Select
                    row_number() over (order by code) as id,
                    *
                from
                    (
                    Select 
                        so.name code,
                        so.date_order date
                    from
                        sale_order so
                    ) vw 
                order by date"""
            % vwName
        )