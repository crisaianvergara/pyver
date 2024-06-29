from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    loan_min = fields.Float("Minimum", config_parameter='pyver_loans.loan_min', default=1000.00)
    loan_max = fields.Float("Maximum", config_parameter='pyver_loans.loan_max', default=100000.00)
    loan_interest = fields.Float("Interest", config_parameter='pyver_loans.loan_interest', default=5.00)

    @api.constrains("loan_min", "loan_max", "loan_interest")
    def _validate_loan_default_fields(self):
        """
        Validate the value of the fields.
        """
        for record in self:
            if record.loan_min <= 0:
                raise ValidationError("Minimum loan amount must be greater than zero.")
            if record.loan_max <= 0:
                raise ValidationError("Maximum loan amount must be greater than zero.")
            if record.loan_interest <= 0:
                raise ValidationError("Loan interest rate must be greater than zero.")
            if record.loan_min == record.loan_max:
                raise ValidationError("Minimum loan amount and maximum loan amount must not be equal.")
            if record.loan_min > record.loan_max:
                raise ValidationError("Minimum loan amount cannot be greater than the maximum loan amount.")