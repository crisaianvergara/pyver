from odoo import fields, models
import time

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
  _inherit = 'res.partner'

  minimum_amount_to_be_paid = fields.Float("Minimum Amount to be Paid")
  matbp_last_updated = fields.Datetime("MATBP Last Updated")

  def _auto_generate_contacts(self, batch_total=20, batch_size=None):
    'Auto generate contacts.'
    _logger.info('function: _auto_generate_contacts')

    for _ in range(batch_total):
      self.with_delay(max_retries=3)._create_contact(records=batch_size)
  
  def _create_contact(self, records):
    data = {
      'name': 'Contact_',
      'function': 'Farmer',
      'email': 'Contact_@gmail.com',
      'phone': '1234567890',
      'mobile': '1234567890',
      'is_company': False,
      'website': 'http://crisaianvergara.com',
    }

    for i in range(records):
      try:
        self.create(data)
        _logger.info(f'Created contact {i + 1}/{records}')
        time.sleep(3)
      except Exception as e:
        _logger.info(f'----- Error creating contact: {e} -----')

  def _auto_update_contacts(self):
    domain = [
      ("name", "=", "Contact_"),
      ("matbp_last_updated", "!=", self._get_date_today()),
    ]
