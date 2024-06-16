import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models

_logger = logging.getLogger(__name__)


class LoanRequest(models.Model):
  _inherit = 'loan.request'

  def _main_auto_generate_invoices(self, records):
    _logger.info('---------- function: _main_auto_generate_invoices ----------')

    for record in records:
      self.main_action_generate_invoice(record)

  def _auto_generate_invoices(self, limit=500):
    _logger.info('---------- function: _auto_generate_invoices ----------')

    date_today = datetime.today()
    result = date_today + relativedelta(months=1)

    result_format = result.strftime('%m/%d/%Y')

    domain = [
      ("date_of_next_invoice", "=", result_format),
      ("state", "=", "approved"),
    ]
    offset = 0

    while True:
      records = self.search(domain, limit=limit, offset=offset)
      
      if not records:
        break
      
      self.with_delay(max_retries=3, description="Loans: Auto Generate Invoices")._main_auto_generate_invoices(records)
      offset += limit
      