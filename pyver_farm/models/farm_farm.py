from odoo import fields, models

class FarmFarm(models.Model):
  _name = "farm.farm"
  _description = "Farm Farm"
  _order = "name"

  name = fields.Char("Name", required=True)
  farm_field_id = fields.Many2one("farm.field", string="Field", required=True)
  farm_crop_id = fields.Many2one("farm.crop", string="Crop", required=True)
  date = fields.Date("Date", default=lambda self:fields.Datetime.now())
