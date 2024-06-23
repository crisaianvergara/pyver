import requests
from odoo import fields, models


class RestPartner(models.Model):
  _inherit = "res.partner"

  facebook_id = fields.Char("Facebook ID")
  def send_facebook_message(self, message):
        messenger_config = self.env['messenger.config'].search([], limit=1)
        if not messenger_config:
            raise ValueError('Messenger configuration not found.')

        url = 'https://graph.facebook.com/v11.0/me/messages'
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'recipient': {'id': self.facebook_id},
            'message': {'text': message}
        }
        params = {
            'access_token': messenger_config.page_access_token
        }

        response = requests.post(url, headers=headers, json=data, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors

        return True