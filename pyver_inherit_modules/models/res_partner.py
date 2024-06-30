from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    barangay = fields.Char(string="Barangay")
    province = fields.Char(string="Province")
    loan_ids = fields.One2many("loan.request", "partner_id", string="Loans")
    loan_count = fields.Integer("Loans", compute="_compute_loan_count")

    @api.depends("loan_ids")
    def _compute_loan_count(self):
        """Count requested loans."""
        for partner in self:
            partner.loan_count = len(partner.loan_ids)
    
    def action_view_partner_loans(self):
        """Redirect to the loan request records of the current partner."""
        self.ensure_one()
        return {
            'name': _('Loans'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
            'res_model': 'loan.request',
        }