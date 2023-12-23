from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    account_move_account_statement_line_ids = fields.One2many("account.statement.line", "account_statement_line_id", string="Statement Lines")
    total_statement_balance = fields.Monetary(string="Total Statement Balance", compute="_compute_statement_balance")
    total_previous_charges = fields.Monetary(string="Total Previous Charges", compute="_compute_statement_balance")


    @api.depends('account_move_account_statement_line_ids')
    def _compute_statement_balance(self):
        for rec in self:
            domain = [
                ("partner_id", "=", rec.partner_id.id),
            ]

            loan_partner = self.env["loan.request"].search(domain, limit=1)

            running_total = []
            running_total.append(loan_partner.unpaid_interest_2023)

            end_date_cutoff = datetime.now() - relativedelta(days=1)

            args = [
                ("partner_id", "=", rec.partner_id.id),
                ("state", "=", "posted"),
                ("move_type", "=", "out_invoice"),
                ("date", "<=", end_date_cutoff)
            ]

            partner_ledger = rec.env["account.move"].search(args, order="date asc")

            for invoice in partner_ledger:
                running_total.append(invoice.amount_total)
            
            rec.total_statement_balance = sum(running_total) + rec.amount_total
            rec.total_previous_charges = rec.total_statement_balance - rec.amount_total


    def action_recompute_statement(self):
        """Call _compute_statement_balance function."""
        self._compute_statement_balance()