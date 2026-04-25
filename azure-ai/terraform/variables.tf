variable "location" {
  description = "Azure region for all resources (resource group, storage, search)"
  type        = string
  default     = "East US"
}

variable "app_location" {
  description = "Azure region for Function App and Static Web App (must support Microsoft.Web)"
  type        = string
  default     = "East US 2"
}

variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
  default     = "rg-resume-ai"
}

variable "project_name" {
  description = "Short project name used as a naming prefix (lowercase letters and numbers only)"
  type        = string
  default     = "resumeai"

  validation {
    condition     = can(regex("^[a-z0-9]{3,16}$", var.project_name))
    error_message = "project_name must be 3-16 lowercase alphanumeric characters (required for globally unique storage account names)."
  }
}

variable "search_sku" {
  description = "Azure AI Search SKU"
  type        = string
  default     = "free"
}

variable "ghcr_username" {
  description = "GitHub username for GitHub Container Registry (ghcr.io)"
  type        = string
  default     = "todd814"
}

variable "ghcr_token" {
  description = "GitHub PAT with read:packages scope — used by Container App to pull image from ghcr.io"
  type        = string
  sensitive   = true
}

variable "inference_endpoint" {
  description = "Azure OpenAI endpoint URL from the Foundry portal (Keys and Endpoint blade) — e.g. https://<resource>.openai.azure.com/"
  type        = string
  sensitive   = true
}

variable "inference_key" {
  description = "Azure OpenAI API key from the Foundry portal (Keys and Endpoint blade)"
  type        = string
  sensitive   = true
}
