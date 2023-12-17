from odoo import api, fields, models


class LoanRequest(models.Model):
    _name = "loan.request"
    _description = "Loan Request"


    name = fields.Char('Number', required=True, index='trigram', copy=False, default='New')
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)


    @api.model
    def create(self, vals):
        """Sequence for Loan Number."""
        vals['name'] = self.env['ir.sequence'].next_by_code('loan.request')
        return super(LoanRequest, self).create(vals)
    



    