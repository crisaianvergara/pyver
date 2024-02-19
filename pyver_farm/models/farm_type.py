from odoo import api, fields, models

class FarmType(models.Model):
  _name = "farm.type"
  _description = "Farm Type"
  _order = "name"

  name = fields.Char("Name", required=True)
