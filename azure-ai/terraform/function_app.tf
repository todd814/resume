# Storage account for Function App internal use (required by Azure Functions runtime)
# Name must be globally unique, 3-24 lowercase alphanumeric characters
resource "azurerm_storage_account" "functions" {
  name                     = "${var.project_name}fnstore"
  resource_group_name      = azurerm_resource_group.resume_ai.name
  location                 = azurerm_resource_group.resume_ai.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # Block all public blob access — the Function runtime accesses via access key
  allow_nested_items_to_be_public = false

  tags = {
    project = "resume-ai"
    managed = "terraform"
  }
}

resource "azurerm_service_plan" "functions" {
  name                = "${var.project_name}-asp"
  resource_group_name = azurerm_resource_group.resume_ai.name
  location            = azurerm_resource_group.resume_ai.location
  os_type             = "Linux"
  sku_name            = "Y1" # Consumption (serverless) plan — pay per execution
}

resource "azurerm_linux_function_app" "ask_resume" {
  name                       = "${var.project_name}-func"
  resource_group_name        = azurerm_resource_group.resume_ai.name
  location                   = azurerm_resource_group.resume_ai.location
  storage_account_name       = azurerm_storage_account.functions.name
  storage_account_access_key = azurerm_storage_account.functions.primary_access_key
  https_only                 = true
  service_plan_id            = azurerm_service_plan.functions.id

  site_config {
    application_stack {
      python_version = "3.11"
    }

    cors {
      # Allow the hosted resume site and the Static Web App chat UI
      allowed_origins = [
        "https://resume.devious.one",
        "https://${azurerm_static_web_app.chat_ui.default_host_name}"
      ]
      support_credentials = false
    }
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME     = "python"
    SCM_DO_BUILD_DURING_DEPLOYMENT = "true"

    AZURE_SEARCH_ENDPOINT        = "https://${azurerm_search_service.resume_search.name}.search.windows.net"
    AZURE_SEARCH_KEY             = azurerm_search_service.resume_search.primary_key
    AZURE_SEARCH_INDEX_NAME      = "resume-content"

    # Phi-4-mini serverless endpoint — set these after creating the endpoint in Azure AI Foundry portal
    # https://ai.azure.com -> My assets -> Model catalog -> Phi-4-mini -> Deploy -> Serverless API
    AZURE_INFERENCE_ENDPOINT     = var.phi4_inference_endpoint
    AZURE_INFERENCE_KEY          = var.phi4_inference_key

    # TODO: Production improvement — move secrets to Azure Key Vault
    # and reference via @Microsoft.KeyVault(SecretUri=...) syntax
  }

  tags = {
    project = "resume-ai"
    managed = "terraform"
  }
}
