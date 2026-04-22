# Phi-4-mini is deployed as a serverless endpoint via Azure AI Foundry (pay-per-token, no reserved capacity).
# Create the endpoint manually in the Azure AI Foundry portal:
#   https://ai.azure.com -> My assets -> Model catalog -> Phi-4-mini -> Deploy -> Serverless API
# Then set these in Terraform Cloud workspace variables (or GitHub secrets for the Function App):
#   AZURE_INFERENCE_ENDPOINT  = the endpoint URL from Foundry
#   AZURE_INFERENCE_KEY       = the API key from Foundry
#
# No Terraform resource needed — serverless endpoints are managed by Azure, not provisioned.
