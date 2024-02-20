from odoo import fields, models

class FarmCrop(models.Model):
  _name = "farm.crop"
  _description = "Farm Crop"
  _order = "name"

  name = fields.Char("Crop", required=True)
  description = fields.Char("Description")
