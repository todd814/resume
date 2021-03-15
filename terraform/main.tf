terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }
  backend "remote" {
    organization = "devious"

    workspaces {
      name = "resume"
    }
  }
}

provider "aws" {
  profile = "default"
  region  = "us-east-1"
}