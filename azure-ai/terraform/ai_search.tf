resource "azurerm_search_service" "resume_search" {
  name                = "${var.project_name}-search"
  resource_group_name = azurerm_resource_group.resume_ai.name
  location            = azurerm_resource_group.resume_ai.location
  sku                 = "free"
  # Free tier: 3 indexes, 50MB, 10K docs/index — sufficient for a resume
  # replica_count and partition_count are fixed at 1 on free tier (cannot be set)

  tags = {
    project = "resume-ai"
    managed = "terraform"
  }
}
