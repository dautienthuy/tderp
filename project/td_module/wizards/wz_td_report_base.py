# -*- encoding: utf-8 -*-

from odoo import api, fields, models


class WzTdReportBase(models.AbstractModel):
    _name = "wz.td.report.base"
    _description = "Wz Td Report Base"
    _report_name = ""

    def print_report(self):
        datas = self.read()[0]
        datas['wizard_report']=True
        res = self.env.ref(self._report_name).with_context(**datas).report_action([], data=[])
        res["close_on_report_download"] = True
        return res
