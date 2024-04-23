from odoo import models
from datetime import datetime
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class LoanRequest(models.Model):
  _inherit = 'loan.request'

  def _auto_generate_invoices(self, limit=None):
    """Auto generate invoices."""
    _logger.info('function: _auto_generate_invoices')

    date_today = datetime.today()
    result = date_today + relativedelta(months=1)

    result_format = result.strftime('%m/%d/%Y')

    domain = [
      ("date_of_next_invoice", "=", result_format),
      ("state", "=", "approved"),
    ]

    records = self.search(domain, limit=limit)

    if records.exists():
      for record in records:
        self.main_action_generate_invoice(record)

    _logger.info("---------- Auto Generating Invoices Completed ----------")




