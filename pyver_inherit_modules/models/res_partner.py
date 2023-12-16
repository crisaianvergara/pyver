from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    barangay = fields.Char(string="Barangay", required=True)
    province = fields.Char(string="Province", required=True)
    