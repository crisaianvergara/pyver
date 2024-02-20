from odoo import fields, models

class FarmLocation(models.Model):
  _name = "farm.location"
  _description = "Farm Location"
  _order = "name"

  name = fields.Char("Location", required=True)
