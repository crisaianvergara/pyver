from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    total_statement_balance = fields.Monetary(string="Total Statement Balance")
    total_previous_charges = fields.Monetary(string="Total Previous Charges")


    def action_recompute_statement(self):
        self.ensure_one()
        for rec in self:
            lines = []
            running_total = []
            running_total.append(0)

            domain = [
                ("partner_id", "=", rec.partner_id.id),
            ]

            loan_partner = self.env["loan.request"].search(domain, limit=1)
            other_charges = loan_partner.loan_request_ids

            for charge in other_charges:
                _logger.info(f"---------- Charge: {charge.name} ----------")
                if charge.state == "unpaid":
                    data = {
                        "name": charge.name,
                        "amount": charge.amount
                    }
                    lines.append(data)
                    running_total.append(charge.amount)
            _logger.info(f"---------- Lines: {lines} ----------")

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
        