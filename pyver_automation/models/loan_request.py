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
      ("payment_structure", "=", "interest_only_loan"),
    ]
    offset = 0

    while True:
      records = self.search(domain, limit=limit, offset=offset)
      if not records:
        break
      self.with_delay(max_retries=3, description="Loans: Auto Generate Invoices")._main_auto_generate_invoices(records)
      offset += limit
  
  def _main_auto_send_outstanding_balance_report(self, records):
    _logger.info('---------- function: _main_auto_send_outstanding_balance_report ----------')

    domain = [
      ("state", "=", "approved"),
      ("payment_structure", "=", "interest_only_loan"),
    ]
    loan_requests = self.search(domain)
    
    for record in records:
      for loan_request in loan_requests:
        if loan_request.partner_id.id == record.partner_id.id:
          try:
            template_id = self.env.ref("pyver_loans.email_template_outstanding_balance_report").id
            self.env['mail.template'].browse(template_id).send_mail(loan_request.id, force_send=True)
          except Exception as e:
            _logger.error(f"('---------- Failed to send email for {loan_request.partner_id.name} - Error: {str(e)} ----------')")

  def _auto_send_outstanding_balance_report(self, limit=100):
    _logger.info('---------- function: _auto_send_outstanding_balance_report ----------')

    domain = [
      ("move_type", "=", "out_invoice"),
      ("state", "<=", "posted"),
      ("invoice_date_due", "=", datetime.today()),
      ("payment_state", "in", ["not_paid", "partial"]),
    ]
    offset = 0

    while True:
      records = self.env["account.move"].search(domain, limit=limit, offset=offset)
      if not records:
        break
      self.with_delay(max_retries=3, description="Loans: Auto Send Outstanding Balance Report")._main_auto_send_outstanding_balance_report(records)
      offset += limit
      