terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  # Terraform Cloud backend — uses a separate workspace from the AWS resume project
  backend "remote" {
    organization = "devious"
    workspaces {
      name = "resume-azure-ai"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "resume_ai" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    project = "resume-ai"
    managed = "terraform"
  }
}
