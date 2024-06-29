def _get_amount_due(rec):
    """Calculate the due/monthly amount to pay."""
    interest_value = rec.loan_amount * (rec.interest_rate  / 100)
    return interest_value

def _get_config_value(self, parameter):
  """Get the default value for the given parameter."""
  return float(self.env['ir.config_parameter'].sudo().get_param(parameter))