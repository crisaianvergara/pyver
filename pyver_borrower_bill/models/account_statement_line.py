from odoo import api, fields, models


class AccountStatementLine(models.Model):
    _name = "account.statement.line"
    _description = "Account Statement Line"

    account_statement_line_id = fields.Many2one("account.move", string="", required=True)
    name = fields.Char(string="Description")
    amount = fields.Float(string="Amount")
    state = fields.Selection(
        string="Statement Type",
        selection=[
            ("previous_charges", "Previous Charges"),
        ],
    )