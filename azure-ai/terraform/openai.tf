# gpt-5-nano is deployed via Azure AI Foundry (pay-per-token, no reserved capacity).
# The Azure OpenAI resource is managed in the Foundry portal — Terraform cannot
# provision Foundry-managed endpoints.
#
# Set these as sensitive variables in your Terraform Cloud workspace:
#   inference_endpoint  = https://todd-resume-3112-resource.openai.azure.com/
#   inference_key       = your Azure OpenAI key (Keys and Endpoint blade)
#
# The deployment name inside the resource must match the model name in function_app.py.
# Verify in Foundry portal: your deployment name for gpt-5-nano.
