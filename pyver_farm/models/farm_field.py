from odoo import api, fields, models

class FarmField(models.Model):
  _name = "farm.field"
  _description = "Farm Field"
  _order = "name"

  name = fields.Char("Name", required=True)
  area = fields.Float("Area (ha)", required=True, default=1.00)
  location = fields.Char("Location", required=True)
  farm_type_id = fields.Many2one("farm.type", string="Farm Type", required=True)
  remarks = fields.Char("Remarks")
