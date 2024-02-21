from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    
    barangay = fields.Char(string="Barangay")
    province = fields.Char(string="Province")
    