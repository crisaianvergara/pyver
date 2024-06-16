import logging
from datetime import datetime

from odoo import models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
  _inherit = 'account.move'

  def _main_auto_post_invoice(self, records):
    _logger.info('---------- function: _main_auto_post_invoice ----------')

    for record in records:
      record.action_recompute_statement()
      record.action_post()

  def _auto_post_invoices(self, limit=100):
    _logger.info('---------- function: _auto_post_invoices ----------')

    domain = [
      ("state", "=", "draft"),
      ("create_date", "<=", datetime.today()),
    ]
    offset = 0

    while True:
      records = self.search(domain, limit=limit, offset=offset)

      if not records:
        break

      self.with_delay(max_retries=3, description="Invoicing: Auto Post Invoices")._main_auto_post_invoice(records)
      offset += limit
        


    