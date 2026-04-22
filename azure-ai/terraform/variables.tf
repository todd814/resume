variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "East US"
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

variable "openai_model_version" {
  description = "Azure OpenAI GPT-4o model version"
  type        = string
  default     = "2024-11-20"
}

variable "openai_capacity" {
  description = "Tokens-per-minute capacity (thousands) for the OpenAI deployment"
  type        = number
  default     = 10
}

variable "search_sku" {
  description = "Azure AI Search SKU — 'basic' supports semantic search"
  type        = string
  default     = "basic"
}
