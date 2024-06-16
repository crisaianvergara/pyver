from odoo import models
from datetime import datetime
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class LoanRequest(models.Model):
  _inherit = 'loan.request'

  def _get_date_today(self):
    """Auto generate invoices."""
    _logger.info('---------- function: _get_date_today ----------')

    date_today = datetime.today()
    result = date_today + relativedelta(months=1)
    result_format = result.strftime('%m/%d/%Y')
    return result_format

  def _auto_generate_invoices(self, limit=None):
    """Auto generate invoices."""
    _logger.info('---------- function: _auto_generate_invoices ----------')

    domain = [
      ("date_of_next_invoice", "=", self._get_date_today()),
      ("state", "=", "approved"),
    ]

    records = self.search(domain, limit=limit)

    if records.exists():
      for record in records:
        self.main_action_generate_invoice(record)
    else:
      _logger.info("---------- No records found! ----------")
    _logger.info("---------- Auto Generating Invoices Completed ----------")




