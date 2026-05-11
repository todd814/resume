# Budget and billing alerts for the resume-ai resource group.
# Alerts fire at 80% actual spend and 100% actual + forecasted spend.
# Notifications go to the email below; no Azure action group required.

resource "azurerm_consumption_budget_resource_group" "resume_ai" {
  name              = "${var.project_name}-budget"
  resource_group_id = azurerm_resource_group.resume_ai.id

  amount     = 5
  time_grain = "Monthly"

  time_period {
    # Starts on the first of the current month; no end date = renews every month
    start_date = formatdate("YYYY-MM-01'T'00:00:00'Z'", timestamp())
  }

  # Alert at 80% of actual spend ($4)
  notification {
    enabled        = true
    threshold      = 80
    threshold_type = "Actual"
    operator       = "GreaterThan"
    contact_emails = ["todd.deblieck@gmail.com"]
  }

  # Alert when actual spend hits 100% ($5)
  notification {
    enabled        = true
    threshold      = 100
    threshold_type = "Actual"
    operator       = "GreaterThan"
    contact_emails = ["todd.deblieck@gmail.com"]
  }

  # Alert when forecasted spend is projected to exceed the budget
  notification {
    enabled        = true
    threshold      = 100
    threshold_type = "Forecasted"
    operator       = "GreaterThan"
    contact_emails = ["todd.deblieck@gmail.com"]
  }

  # Prevent Terraform from updating the start_date on every apply
  # (timestamp() changes each run, but the budget itself doesn't need to move)
  lifecycle {
    ignore_changes = [time_period]
  }
}
