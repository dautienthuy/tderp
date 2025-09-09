from odoo import models, fields

class MaintenanceTarget(models.Model):
    _name = "maintenance.target"
    _description = "Maintenance KPI Target per Employee"

    employee_id = fields.Many2one("hr.employee", string="Nhân viên", required=True)
    month = fields.Selection(
        [(str(m), str(m)) for m in range(1, 13)],
        string="Tháng", required=True
    )
    year = fields.Integer(string="Năm", required=True, default=lambda self: fields.Date.today().year)

    # Chỉ tiêu
    target_requests = fields.Integer(string="Chỉ tiêu xử lý", default=0)
    target_days = fields.Integer(string="Chỉ tiêu ngày làm việc", default=0)

    # Liên kết với request thực tế
    request_ids = fields.One2many("maintenance.request", "target_id", string="Requests")
    achieved_requests = fields.Integer(string="Đã xử lý", compute="_compute_achieved", store=True)
    achieved_days = fields.Integer(string="Ngày LV", compute="_compute_achieved", store=True)

    progress = fields.Float(string="Tiến độ (%)", compute="_compute_progress", store=True)

    def _compute_achieved(self):
        for rec in self:
            reqs = rec.request_ids.filtered(lambda r: r.stage_id.name == "Done")
            rec.achieved_requests = len(reqs)
            rec.achieved_days = len({r.request_date.date() for r in reqs if r.request_date})

    def _compute_progress(self):
        for rec in self:
            rec.progress = 0
            if rec.target_requests:
                rec.progress = 100.0 * rec.achieved_requests / rec.target_requests
