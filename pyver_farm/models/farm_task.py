from odoo import fields, models

class FarmTask(models.Model):
  _name = "farm.task"
  _description = "Farm Task"
  _order = "name"

  name = fields.Char("Task", required=True)
  description = fields.Char("Description")
