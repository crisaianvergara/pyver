import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from .utils import _get_amount_due, _get_config_value

_logger = logging.getLogger(__name__)


class LoanRequest(models.Model):
    _name = "loan.request"
    _description = "Loan Request"
    _order = "name"
    _rec_name = "partner_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Number", required=True, index="trigram", copy=False, default="New")
    partner_id = fields.Many2one("res.partner", string="Partner", required=True, tracking=True)
    loan_amount = fields.Float("Amount", required=True, default=lambda self: self._default_loan_min(), tracking=True)
    loan_type_id = fields.Many2one("loan.type", string="Loan Type", required=True, tracking=True)
    interest_rate = fields.Float("Interest Rate (%)", required=True, default=lambda self: self._default_loan_interest(), tracking=True)
    amount_due = fields.Float("Amount Due", compute="_compute_amount_due")
    payment_structure = fields.Selection(
        string="Payment Structure",
        copy=False,
        default="interest_only_loan",
        required=True,
        selection=[
            ("amortized_loan", "Amortized Loan"),
            ("interest_only_loan", "Interest-Only Loan"),
            ("interest_free_loan", "Interest-Free Loan"),
        ],
        tracking=True,
        help="Select the type of loan payment structure:\n"
             "- Amortized Loan: Regular payments covering both principal and interest.\n"
             "- Interest-Only Loan: Initial payments cover only the interest, with principal payments starting later.\n"
             "- Interest-Free Loan: No interest charged, only repay the principal amount borrowed.",
    )
    applied_date = fields.Date("Applied Date")
    approved_date = fields.Date("Approved Date")
    fully_paid_date = fields.Date("Fully Paid Date", tracking=True)
    date_of_next_invoice = fields.Date("Date of Next Invoice", compute="_compute_date_of_next_invoice", store=True)
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
        tracking=True,
    )
    related_loan_ids = fields.One2many(
        "loan.request", "partner_id",
        string="Related Loans",
        compute="_compute_related_loans"
    )
    borrowed_date = fields.Date("Borrowed Date", default=lambda self: fields.Datetime.now(), tracking=True)
    loan_request_ids = fields.One2many("other.charge", "other_charge_id", string="Other Charges")
    borrower_invoice_ids = fields.One2many(
        "account.move", "partner_id",
        compute="_compute_borrower_invoice_ids",
        string="Borrower Invoices"
    )
    notes = fields.Html(string="Notes")
    
    @api.model
    def create(self, vals):
        """Sequence for Loan Number."""
        vals["name"] = self.env["ir.sequence"].next_by_code("loan.request")
        return super(LoanRequest, self).create(vals)
    
    @api.depends("loan_amount", "interest_rate")
    def _compute_amount_due(self):
        """Compute amount due."""
        for rec in self:
            if rec.loan_amount > 0 and rec.interest_rate > 0:
                rec.amount_due = _get_amount_due(rec)
            else: 
                rec.amount_due = 0
    
    @api.depends("approved_date")
    def _compute_date_of_next_invoice(self):
        """Compute date of next invoice."""
        for rec in self:
            if rec.approved_date:
                rec.date_of_next_invoice = rec.approved_date + relativedelta(months=1)
            else:
                rec.date_of_next_invoice = None

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

    @api.depends("partner_id")
    def _compute_borrower_invoice_ids(self):
        """"
        Fetch the invoices related to the borrower.
        """
        for rec in self:
            rec.borrower_invoice_ids = self.env["account.move"].search(
                [
                    ("partner_id", "=", rec.partner_id.id),
                    ("move_type", "=", "out_invoice"),
                    ("state", "=", "posted"),
                    ("payment_state", "in", ["not_paid", "partial"]),
                    ("invoice_date_due", "<", fields.Date.today())
                ]
            )

    @api.constrains("interest_rate")
    def _validate_interest_rate_field(self):
        """Validate the interest rate field."""
        for record in self:
            if record.interest_rate < 0:
                raise ValidationError("Interest rate must not be negative.")
            
    @api.constrains("fully_paid_date")
    def _validate_fully_paid_date(self):
        """
        Check if the fully paid date in the past or current day. 
        """
        for record in self:
            if record.fully_paid_date and record.fully_paid_date > fields.Date.today():
                raise ValidationError("Fully paid date must be today or in the past.")
    
    @api.constrains("borrowed_date")
    def _validate_borrowed_date(self):
        """
        Check if the borrowed date in the past or current day. 
        """
        for record in self:
            if record.borrowed_date and record.borrowed_date > fields.Date.today():
                raise ValidationError("Borrowed date must be today or in the past.")

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
        """Validate loan amount: must be between minimum and maximum loan."""
        for rec in self:
            if rec.state != "fully_paid":
                loan_min = _get_config_value(self, 'pyver_loans.loan_min')
                loan_max = _get_config_value(self, 'pyver_loans.loan_max')
                if not loan_min <= rec.loan_amount <= loan_max:
                    raise ValidationError(f"Amount must be in between {loan_min:,.2f} to {loan_max:,.2f}.")
                
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

    def action_fully_paid(self):
        """Fully paid borrow/loan application."""
        vals = {
            "state": "fully_paid",
            "fully_paid_date": datetime.now(),
            "loan_amount": 0.00,
        }
        for rec in self:
            rec.write(vals)

    def action_cancel(self):
        """Cancel borrow/loan application."""
        if "approved" in self.mapped("state"):
            raise ValidationError("Approved borrows cannot be cancel.")
        return self.write({"state": "canceled"})

    def action_reset_to_draft(self):
        """Reset loan request to draft state."""
        self.write({"state": "draft"})
        return {}
    
    def action_generate_invoice(self):
        for rec in self:
            self.main_action_generate_invoice(rec)

    def _default_loan_min(self):
        """Get the the default loan amount."""
        return _get_config_value(self, 'pyver_loans.loan_min')
    
    def _default_loan_interest(self):
        """Get the the default loan interest."""
        return _get_config_value(self, 'pyver_loans.loan_interest')

    def main_action_generate_invoice(self, rec):
        """Generate invoice."""
        _logger.info("---------- Generating Invoices ----------")

        product = self.get_product()

        _logger.info(f"---------- Create Invoice ----------")
        data = {
            "partner_id": rec.partner_id.id,
            "invoice_date_due": rec.date_of_next_invoice,
            "move_type": "out_invoice",
        }

        new_invoice = self.env["account.move"].create(data)
        _logger.info(f"---------- Invoice {new_invoice.id} generated successfully. ----------")

        _logger.info(f"---------- Create Invoice Lines ----------")
        invoice_line_data = {
            "move_id": new_invoice.id,
            "product_id": product.id,
            "price_unit": rec.amount_due,
        }

        new_invoice_line = self.env["account.move.line"].create(invoice_line_data)
        _logger.info(f"---------- Invoice Line {new_invoice_line.id} created for Invoice {new_invoice.id}. ----------")
        
        _logger.info(f"---------- Update Date of Next Invoice ----------")
        update_date_of_next_invoice = rec.date_of_next_invoice + relativedelta(months=1)
        rec.write({"date_of_next_invoice": update_date_of_next_invoice})
        rec.message_post(body="Invoice has been generated successfully.")

    def get_product(self):
        _logger.info("---------- Search Product ----------")
        product = self.env["product.template"].search([
            ("name", "=", "Loan Interest")
        ], limit=1)
        _logger.info(f"---------- Product: {product}. ----------")

        if not product:
            _logger.info(f"---------- Create Product ----------")
            data = {
                "name": "Loan Interest",
                "list_price": 0.00,
                "taxes_id": False,
                "supplier_taxes_id": False,
            }
            product = self.env["product.template"].create(data)
            _logger.info(f"---------- Product {product.id} created. ----------")
            _logger.info(f"---------- Product INFO {product.id}. ----------")
            return product
        
        _logger.info(f"---------- Product INFO {product.id}. ----------")
        return product
