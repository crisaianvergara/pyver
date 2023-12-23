from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    account_move_account_statement_line_ids = fields.One2many("account.statement.line", "account_statement_line_id", string="")
    total_statement_balance = fields.Monetary(string="Total Statement Balance")
    total_previous_charges = fields.Monetary(string="Total Previous Charges")


    def action_recompute_statement(self):
        """Recompute statement lines."""
        raise ValidationError("Recompute Statement Lines.")