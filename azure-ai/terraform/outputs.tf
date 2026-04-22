output "function_app_url" {
  description = "Base URL of the Azure Function App — set AZURE_FUNCTION_URL in chat-ui with this value"
  value       = "https://${azurerm_linux_function_app.ask_resume.default_hostname}/api/ask"
}

output "static_web_app_url" {
  description = "URL of the hosted chat UI"
  value       = "https://${azurerm_static_web_app.chat_ui.default_host_name}"
}

output "static_web_app_api_token" {
  description = "Deployment token for the Static Web App — store as AZURE_STATIC_WEB_APPS_API_TOKEN in GitHub secrets"
  value       = azurerm_static_web_app.chat_ui.api_key
  sensitive   = true
}

output "search_service_name" {
  description = "Azure AI Search service name — used by the indexing script"
  value       = azurerm_search_service.resume_search.name
}

output "search_admin_key" {
  description = "Azure AI Search admin key — used by the indexing script (AZURE_SEARCH_KEY)"
  value       = azurerm_search_service.resume_search.primary_key
  sensitive   = true
}

output "openai_endpoint" {
  description = "Azure OpenAI endpoint"
  value       = azurerm_cognitive_account.openai.endpoint
}

output "resource_group_name" {
  description = "Resource group name — used to scope Azure CLI commands"
  value       = azurerm_resource_group.resume_ai.name
}
