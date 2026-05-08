# VNet networking for the AI Foundry / Azure OpenAI resource.
#
# Uses VNet Service Endpoints (Microsoft.CognitiveServices) rather than Private
# Endpoints. Both approaches keep inference traffic on the Microsoft backbone;
# the difference is cost:
#   - Private Endpoint: ~$0.01/hr per endpoint (~$7/month) + data fees
#   - VNet Service Endpoint: FREE
#
# After applying, restrict the OpenAI resource in the Foundry portal:
#   Networking blade → "Selected networks" → add the container-apps subnet.
# This ensures only the Container App (via its VNet subnet) can call the API.

# ---------------------------------------------------------------------------
# Virtual Network
# ---------------------------------------------------------------------------
resource "azurerm_virtual_network" "resume_ai" {
  name                = "${var.project_name}-vnet"
  location            = var.app_location
  resource_group_name = azurerm_resource_group.resume_ai.name
  address_space       = ["10.0.0.0/16"]

  tags = {
    project = "resume-ai"
    managed = "terraform"
  }
}

# ---------------------------------------------------------------------------
# Subnet — Container App Environment
#
# Requires a dedicated /23 (or larger) with a delegation to Microsoft.App.
# The Microsoft.CognitiveServices service endpoint is enabled here so that
# outbound calls to Azure OpenAI stay on the Microsoft backbone at no charge.
# ---------------------------------------------------------------------------
resource "azurerm_subnet" "container_apps" {
  name                 = "snet-container-apps"
  resource_group_name  = azurerm_resource_group.resume_ai.name
  virtual_network_name = azurerm_virtual_network.resume_ai.name
  address_prefixes     = ["10.0.0.0/23"]

  # Free service endpoint — routes Cognitive Services traffic over the
  # Microsoft backbone without a per-hour private endpoint charge.
  service_endpoints = ["Microsoft.CognitiveServices"]

  delegation {
    name = "container-apps-delegation"
    service_delegation {
      name    = "Microsoft.App/environments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}
