# -*- encoding: utf-8 -*-

from odoo import api, fields, models, tools


class WzTdReportSale(models.TransientModel):
    _name = 'wz.td.report.sale'
    _description = "Wz Td Report Sale"
    _rec_name = "date_from"

    date_from = fields.Date(u'Từ ngày')
    date_to = fields.Date(u'Đến ngày')
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    detail_ids = fields.One2many("wz.td.report.sale.detail", compute="_get_detail_list", string=u"Danh sách")
    state = fields.Selection([('draft', 'Báo giá'),('sale', 'Đơn hàng'), ('all', 'Đầy đủ')], string='Trạng thái', default='all')

    def compute(self):
        return {"tag": "reload", "type": "ir.actions.act_window_close"}

    def _get_detail_list(self):
        cr = self._cr
        for obj in self.filtered(lambda obj: obj.date_from and obj.date_to):
            date_from = obj.date_from
            date_to = obj.date_to

            a_state = ''
            if obj.state != 'all':
                a_state = " and state = '%s'" % obj.state
            sqlCommand = """Select
                            distinct
                            tdsd.id,
                            code,
                            date
                        from
                            wz_td_report_sale_detail tdsd
                        where
                            date between '{date_from}' and '{date_to}'
                            {a_state}
                        order by
                            date
                            """.format(
                date_from=date_from, date_to=date_to, a_state=a_state
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
    rp_name = fields.Char("Khách hàng")
    client_code = fields.Char("Hợp đồng khách")
    amount_total = fields.Float("Giá trị hợp đồng")
    amount_payment = fields.Float("Thanh toán")
    amount_paid = fields.Float("Công nợ")
    street = fields.Char('Địa chỉ')
    phone = fields.Char('SĐT KH')
    other_phone = fields.Char('SĐT Xây dựng')
    feature = fields.Char('Đặc tính')
    duration_contract = fields.Date("Tiến độ hợp đồng")
    work_progress = fields.Text('Tiến độ Thi công')
    est_progress = fields.Text('Mốc dự kiến')
    moving_plan = fields.Date('Kế hoạch lên nhà mới')
    date = fields.Date("Ngày đặt hàng")
    commitment_date = fields.Date("Ngày hàng về")
    date_done = fields.Date("Ngày kiểm định, bàn giao")
    state = fields.Char('Trạng thái')

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
                        rp.name rp_name,
                        so.name code,
                        so.date_order date,
                        so.client_code client_code,
                        so.amount_total,
                        (select sum(total_paid) from sale_payment_term where order_id = so.id) amount_payment,
                        (so.amount_total - 
                            COALESCE((select sum(total_paid) from sale_payment_term where order_id = so.id), 0)
                        ) amount_paid,
                        rp.street street,
                        rp.phone phone,
                        rp.phone other_phone,
                        so.feature,
                        so.duration_contract,
                        array_to_string(array_agg(to_char(sep.date, 'DD-MM-YYYY')||': '||sep.name),E'\n') work_progress,
                        max(est_progress) est_progress,
                        sp.date moving_plan,
                        so.commitment_date commitment_date,
                        so.date_done date_done,
                        so.state
                    from
                        sale_order so
                    left join
                        res_partner rp on so.partner_id = rp.id
                    left join
                        sale_plan sp on so.id = sp.order_id
                    left join
                        sale_excurtion_progress sep on sp.id = sep.sale_plan_id
                    left join
                        (
                            select
                                sale_plan_id,
                                array_to_string(array_agg(to_char(date, 'DD-MM-YYYY')||': '||name),E'\n') est_progress
                            from
                                sale_construction_schedule
                            group by sale_plan_id
                    ) vwscs on vwscs.sale_plan_id = sp.id
                    group by so.id, rp.id, sp.id, vwscs.sale_plan_id
                    ) vw 
                order by date"""
            % vwName
        )