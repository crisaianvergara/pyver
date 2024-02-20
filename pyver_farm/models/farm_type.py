from odoo import fields, models

class FarmType(models.Model):
  _name = "farm.type"
  _description = "Farm Type"
  _order = "name"

  name = fields.Char("Type", required=True)
