from odoo import fields, models

class FarmType(models.Model):
  _name = "farm.uom"
  _description = "Farm Uom"
  _order = "name"

  name = fields.Char("Units of Measure", required=True)
  description = fields.Char("Description", required=True)
