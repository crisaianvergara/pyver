from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LoanType(models.Model):
    _name = "loan.type"
    _description = "Loan Type"
    _order = 'code'

    code = fields.Char('Code', required=True, index='trigram', copy=False, default='New')
    name = fields.Char("Name", required=True)

    # Python Constraints
    @api.constrains("name")
    def _validate_name(self):
        """Validate name."""
        for rec in self:
            if len(rec.name) < 3:
                raise ValidationError("Type must be greater than 3 characters.")
            
            same_name_records = self.search(
                [('name', '=ilike', rec.name), ('id', '!=', rec.id)]
            )
            if same_name_records:
                raise ValidationError(f"The loan type '{rec.name}' already exists.")
    
    @api.model
    def create(self, vals):
        """Sequence for Code."""
        vals['code'] = self.env['ir.sequence'].next_by_code('loan.type')
        return super(LoanType, self).create(vals)