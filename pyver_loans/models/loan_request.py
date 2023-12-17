from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError

LOAN_AMOUNT_MIN = 5000
LOAN_AMOUNT_MAX = 50000
LOAN_INTEREST_MIN = 5


def get_amount_due(rec):
    """Calculate the amount due/monthly amount to pay."""
    interest_value = rec.loan_amount * (rec.interest_rate  / 100)
    return interest_value


class LoanRequest(models.Model):
    _name = "loan.request"
    _description = "Loan Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Number', required=True, index='trigram', copy=False, default='New')
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    loan_amount = fields.Float("Amount", required=True, default=LOAN_AMOUNT_MIN)
    loan_type_id = fields.Many2one("loan.type", string="Loan Type", required=True)
    interest_rate = fields.Float("Interest Rate (%)", required=True, default=LOAN_INTEREST_MIN)
    amount_due = fields.Float("Amount Due", compute="_compute_amount_due")
    applied_date = fields.Date("Applied Date")
    approved_date = fields.Date("Approved Date")
    state = fields.Selection(
        string="Status",
        copy=False,
        default="draft",
        required=True,
        selection=[
            ("draft", "Draft"),
            ("applied", "Applied"),
            ("approved", "Approved"),
            ("fully_paid", "Fully Paid"),
            ("canceled", "Canceled"),
        ],
    )
    related_loan_ids = fields.One2many(
        "loan.request", "partner_id",
        string="Related Loans",
        compute="_compute_related_loans"
    )


    @api.model
    def create(self, vals):
        """Sequence for Loan Number."""
        vals['name'] = self.env['ir.sequence'].next_by_code('loan.request')
        return super(LoanRequest, self).create(vals)
    

    @api.depends("loan_amount", "interest_rate")
    def _compute_amount_due(self):
        """Compute amount due."""
        for rec in self:
            if rec.loan_amount > 0 and rec.interest_rate > 0:
                rec.amount_due = get_amount_due(rec)
            else: 
                rec.amount_due = 0


    @api.depends("partner_id")
    def _compute_related_loans(self):
        """
        Compute related loans for the borrower.
        Connected to related_loan_ids(field) and _validate_related_loans(Python Constraints)
        """
        for rec in self:
            related_loans = self.search(
                [
                    ("partner_id", "=", rec.partner_id.id),
                    ("id", "!=", rec.id),
                    ("state", "in", ["draft", "applied", "approved"])
                ]
            )
            rec.related_loan_ids = related_loans
                

    @api.constrains("state")
    def _validate_related_loans(self):
        """
        Validate related loan.
        If the partner has an active loan: raise Validation.
        """
        for rec in self:
            if rec.related_loan_ids and rec.state not in ["canceled"]:
                raise ValidationError("The borrower already has an active loan.")
            

    @api.constrains("loan_amount")
    def _validate_loan_amount(self):
        """Validate loan amount: must be between LOAN_AMOUNT_MIN and LOAN_AMOUNT_MAX loan."""
        for rec in self:
            if not LOAN_AMOUNT_MIN <= rec.loan_amount <= LOAN_AMOUNT_MAX:
                raise ValidationError(f"Amount must be in between {LOAN_AMOUNT_MIN} to {LOAN_AMOUNT_MAX}.")
            
            
    def action_apply(self):
        """Apply loan application."""
        vals = {
            "state": "applied",
            "applied_date": datetime.now(),
        }
        if "canceled" in self.mapped("state"):
            raise ValidationError("Canceled loans cannot be submit.")
        return self.write(vals)
    

    def action_approve(self):
        """Approved borrow/loan application."""
        vals = {
            "state": "approved",
            "approved_date": datetime.now(),
        }
        for rec in self:
            rec.write(vals)

    
    def action_cancel(self):
        """Cancel borrow/loan application."""
        if "approved" in self.mapped("state"):
            raise ValidationError("Approved borrows cannot be cancel.")
        return self.write({"state": "canceled"})