from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LoanType(models.Model):
    _name = "loan.type"
    _description = "Loan Type"
    _order = 'name'

    # SQL Constraints
    _sql_constraints = [
        ("check_unique_name", "UNIQUE(name)", "The Type must be unique."),
    ]

    # Fields
    name = fields.Char("Name", required=True)
    code = fields.Char('Code', required=True, index='trigram', copy=False, default='New')


    # Python Constraints
    @api.constrains("name")
    def _validate_name(self):
        """Validate name."""
        for rec in self:
            if len(rec.name) < 3:
                raise ValidationError("Type must be greater than 3 characters.")
    

    @api.model
    def create(self, vals):
        """Sequence for Code."""
        vals['code'] = self.env['ir.sequence'].next_by_code('loan.type')
        return super(LoanType, self).create(vals)