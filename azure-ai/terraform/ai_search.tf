resource "azurerm_search_service" "resume_search" {
  name                = "${var.project_name}-search"
  resource_group_name = azurerm_resource_group.resume_ai.name
  location            = azurerm_resource_group.resume_ai.location
  sku                 = var.search_sku
  replica_count       = 1
  partition_count     = 1

  # Semantic search is included in basic+ SKUs at no extra cost
  semantic_search_sku = "free"

  tags = {
    project = "resume-ai"
    managed = "terraform"
  }
}
