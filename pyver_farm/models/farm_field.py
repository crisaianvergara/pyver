from odoo import fields, models

class FarmField(models.Model):
  _name = "farm.field"
  _description = "Farm Field"
  _order = "name"

  name = fields.Char("Field", required=True)
  area = fields.Float("Area (ha)", required=True, default=1.00)
  farm_location_id = fields.Many2one("farm.location", string="Location", required=True)
  farm_type_id = fields.Many2one("farm.type", string="Type", required=True)
  remarks = fields.Char("Remarks")
