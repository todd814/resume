resource "azurerm_static_web_app" "chat_ui" {
  name                = "${var.project_name}-swa"
  resource_group_name = azurerm_resource_group.resume_ai.name
  location            = azurerm_resource_group.resume_ai.location
  sku_tier            = "Free"
  sku_size            = "Free"

  tags = {
    project = "resume-ai"
    managed = "terraform"
  }
}
