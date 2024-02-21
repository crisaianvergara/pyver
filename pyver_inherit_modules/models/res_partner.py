from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    barangay = fields.Char(string="Barangay")
    province = fields.Char(string="Province")
    