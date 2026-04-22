# NOTE: Azure OpenAI requires approved access on your subscription.
# Request access at: https://aka.ms/oai/access
# Availability varies by region — East US and East US 2 have the widest model availability.

resource "azurerm_cognitive_account" "openai" {
  name                = "${var.project_name}-openai"
  resource_group_name = azurerm_resource_group.resume_ai.name
  location            = azurerm_resource_group.resume_ai.location
  kind                = "OpenAI"
  sku_name            = "S0"

  tags = {
    project = "resume-ai"
    managed = "terraform"
  }
}

resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = "gpt-4o"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = var.openai_model_version
  }

  scale {
    type     = "Standard"
    capacity = var.openai_capacity
  }
}
