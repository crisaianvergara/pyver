from odoo import api, fields, models


class OtherCharge(models.Model):
    _name = "other.charge"
    _description = "Other Charge"

    other_charge_id = fields.Many2one("loan.request", string="Other Charges", required=True)
    name = fields.Char(string="Description", required=True)
    amount = fields.Float(string="Amount", required=True)
    state = fields.Selection(
        string="Status",
        copy=False,
        default="not_paid",
        required=True,
        selection=[
            ("paid", "Paid"),
            ("not_paid", "Not Paid"),
        ],
    )