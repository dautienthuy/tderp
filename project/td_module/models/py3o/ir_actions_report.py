from odoo import api, fields, models, _

try:
    from py3o.formats import Formats
except ImportError:
    logger.debug("Cannot import py3o.formats")


class IrActionsReport(models.Model):
    """ Inherit from ir.actions.report to add new XLSX output
    """

    _inherit = "ir.actions.report"

    @api.model
    def _get_py3o_filetypes(self):
        """
            Add new xlsx to format output
        """
        res = super(__class__, self)._get_py3o_filetypes() or []
        excelFiles = [("xlsx", "Excel (xlsx)")]
        return res + excelFiles

    @api.depends("report_type", "py3o_filetype")
    def _compute_is_py3o_native_format(self):
        formats = Formats()
        names = formats.get_known_format_names()
        for rec in self:
            filetype = rec.py3o_filetype
            if filetype in names:
                super(__class__, rec)._compute_is_py3o_native_format()
            else:
                rec.is_py3o_native_format = ""
