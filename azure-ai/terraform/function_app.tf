# Log Analytics workspace — required by Container App Environment
# Free tier: 5 GB/day ingestion — well within free limits for a resume chatbot
resource "azurerm_log_analytics_workspace" "resume_ai" {
  name                = "${var.project_name}-logs"
  location            = var.app_location
  resource_group_name = azurerm_resource_group.resume_ai.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = {
    project = "resume-ai"
    managed = "terraform"
  }
}

# Container App Environment — the shared networking/logging plane
resource "azurerm_container_app_environment" "resume_ai" {
  name                       = "${var.project_name}-env"
  location                   = var.app_location
  resource_group_name        = azurerm_resource_group.resume_ai.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.resume_ai.id

  tags = {
    project = "resume-ai"
    managed = "terraform"
  }
}

# Container App — runs the FastAPI ask-resume service
# Initial image is a public placeholder; GitHub Actions deploys the real image after first push
resource "azurerm_container_app" "ask_resume" {
  name                         = "${var.project_name}-app"
  container_app_environment_id = azurerm_container_app_environment.resume_ai.id
  resource_group_name          = azurerm_resource_group.resume_ai.name
  revision_mode                = "Single"

  # ghcr.io credentials so Azure can pull the private container image
  registry {
    server               = "ghcr.io"
    username             = var.ghcr_username
    password_secret_name = "ghcr-token"
  }

  secret {
    name  = "ghcr-token"
    value = var.ghcr_token
  }

  secret {
    name  = "search-key"
    value = azurerm_search_service.resume_search.primary_key
  }

  secret {
    name  = "inference-endpoint"
    value = var.inference_endpoint
  }

  secret {
    name  = "inference-key"
    value = var.inference_key
  }

  template {
    min_replicas = 0 # Scale to zero when idle — no charge when not in use
    max_replicas = 1

    container {
      name   = "ask-resume"
      image  = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "AZURE_SEARCH_ENDPOINT"
        value = "https://${azurerm_search_service.resume_search.name}.search.windows.net"
      }
      env {
        name        = "AZURE_SEARCH_KEY"
        secret_name = "search-key"
      }
      env {
        name  = "AZURE_SEARCH_INDEX_NAME"
        value = "resume-content"
      }
      env {
        name        = "AZURE_INFERENCE_ENDPOINT"
        secret_name = "inference-endpoint"
      }
      env {
        name        = "AZURE_INFERENCE_KEY"
        secret_name = "inference-key"
      }
      env {
        name  = "ALLOWED_ORIGINS"
        value = "https://${azurerm_static_web_app.chat_ui.default_host_name},https://resume.devious.one"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  # GitHub Actions updates the container image via `az containerapp update`.
  # This prevents terraform apply from reverting the image back to the placeholder.
  lifecycle {
    ignore_changes = [template[0].container[0].image]
  }

  tags = {
    project = "resume-ai"
    managed = "terraform"
  }
}
