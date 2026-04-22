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

variable "search_sku" {
  description = "Azure AI Search SKU"
  type        = string
  default     = "free"
}

variable "phi4_inference_endpoint" {
  description = "Phi-4-mini serverless endpoint URL from Azure AI Foundry"
  type        = string
  sensitive   = true
}

variable "phi4_inference_key" {
  description = "Phi-4-mini serverless endpoint API key from Azure AI Foundry"
  type        = string
  sensitive   = true
}
