resource "azurerm_static_web_app" "chat_ui" {
  name                = "${var.project_name}-swa"
  resource_group_name = azurerm_resource_group.resume_ai.name
  location            = var.app_location
  sku_tier            = "Free"
  sku_size            = "Free"

  tags = {
    project = "resume-ai"
    managed = "terraform"
  }
}

resource "azurerm_static_web_app_custom_domain" "chat_ui" {
  static_web_app_id = azurerm_static_web_app.chat_ui.id
  domain_name       = "ask.todd.deblieck.me"
  validation_type   = "cname-delegation"
}
