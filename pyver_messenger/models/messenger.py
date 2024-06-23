from odoo import api, fields, models


class Messenger(models.Model):
  _name ="messenger"
  _description = "Messenger"

  name = fields.Char('Name', required=True)
  page_access_token = fields.Char("Page Access Token", required=True)