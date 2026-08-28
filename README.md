# TicketTriage

AI-powered helpdesk system. Students submit support tickets, Azure AI auto-categorises them, admins review and manage the queue.

**Live:** https://witty-dune-0dbfce600.7.azurestaticapps.net

---

## Setup

### Prerequisites

- Python 3.11+
- Azure Functions Core Tools (`npm install -g azure-functions-core-tools@4`)

### Steps

1. Clone and enter the repo:
```bash
git clone https://github.com/kerjing0328/ticket-triage-g1.git
cd ticket-triage-g1
```

2. Set up the API:
```bash
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy local.settings.json.sample local.settings.json
```

3. Edit `api/local.settings.json` and add your Azure keys (see Environment Variables below).

4. Start the API:
```bash
func start --cors "*"
```

5. In a separate terminal, serve the frontend:
```bash
python -m http.server 3000 --directory frontend
```

6. Open in browser:
- Ticket form: http://localhost:3000
- Admin dashboard: http://localhost:3000/admin.html

7. (Optional) Load sample data:
```bash
python scripts/seed_api.py http://localhost:7071/api
```

---

## Deployment

Push to `main` to trigger GitHub Actions. Tests run first, then deploys to Azure Static Web Apps.

```bash
git add . && git commit -m "deploy" && git push
```

### Check Status

- GitHub Actions: https://github.com/kerjing0328/ticket-triage-g1/actions
- Live App: https://witty-dune-0dbfce600.7.azurestaticapps.net

### Create All Azure Resources

```bash
RG=rg-ticket-triage
LOCATION=eastasia

# 1. Resource Group
az group create -n $RG -l $LOCATION

# 2. Cosmos DB (free tier)
az cosmosdb create -n cosmos-ticket-triage-g1 -g $RG \
  --kind GlobalDocumentDB --enable-free-tier true --locations regionName=$LOCATION

# 3. Cosmos DB database and container
az cosmosdb sql database create -a cosmos-ticket-triage-g1 -g $RG \
  -n Helpdesk
az cosmosdb sql container create -a cosmos-ticket-triage-g1 -g $RG \
  -d Helpdesk -n Tickets --partition-key-path "/category" --throughput 400

# 4. AI Language (free tier)
az cognitiveservices account create -n language-ticket-triage-g1 -g $RG \
  --kind TextAnalytics --sku F0 --location $LOCATION

# 5. Key Vault (RBAC enabled)
az keyvault create -n kv-ticket-triage-g1 -g $RG --enable-rbac-authorization true

# 6. Static Web App
az staticwebapp create -n swa-ticket-triage -g $RG \
  --source https://github.com/kerjing0328/ticket-triage-g1.git \
  --branch main \
  --app-location "frontend" --api-location "api" \
  --sku Free --location $LOCATION
```

### Configure Secrets

```bash
RG=rg-ticket-triage

# Get AI Language keys
AI_ENDPOINT=$(az cognitiveservices account show -n language-ticket-triage-g1 -g $RG --query "properties.endpoint" -o tsv)
AI_KEY=$(az cognitiveservices account keys list -n language-ticket-triage-g1 -g $RG --query "key1" -o tsv)

# Get Cosmos DB connection string
COSMOS_CONN=$(az cosmosdb keys list -n cosmos-ticket-triage-g1 -g $RG --query "primaryConnectionString" -o tsv)

# Store secrets in Key Vault
az keyvault secret set -n COSMOS_CONNECTION_STRING --vault-name kv-ticket-triage-g1 --value "$COSMOS_CONN"
az keyvault secret set -n AI_LANGUAGE_ENDPOINT --vault-name kv-ticket-triage-g1 --value "$AI_ENDPOINT"
az keyvault secret set -n AI_LANGUAGE_KEY --vault-name kv-ticket-triage-g1 --value "$AI_KEY"

# Service principal for Key Vault access
APP_ID=$(az ad app create --display-name "tickettriage-kv-access" --query "appId" -o tsv)
az ad sp create --id $APP_ID
SECRET=$(az ad app credential reset --id $APP_ID --append --end-date "2027-01-01" --query "password" -o tsv)
TENANT=$(az account show --query "tenantId" -o tsv)

az role assignment create --assignee $APP_ID \
  --role "Key Vault Secrets User" \
  --scope /subscriptions/$(az account show --query "id" -o tsv)/resourceGroups/$RG/providers/Microsoft.KeyVault/vaults/kv-ticket-triage-g1

# Store in Static Web App settings
az staticwebapp appsettings set -n swa-ticket-triage -g $RG --setting-names \
  COSMOS_CONNECTION_STRING="$COSMOS_CONN" \
  AI_LANGUAGE_ENDPOINT="$AI_ENDPOINT" \
  AI_LANGUAGE_KEY="$AI_KEY" \
  AZURE_CLIENT_ID="$APP_ID" \
  AZURE_CLIENT_SECRET="$SECRET" \
  AZURE_TENANT_ID="$TENANT" \
  KEY_VAULT_URL="https://kv-ticket-triage-g1.vault.azure.net/"
```

---

## Environment Variables

### Local Development

Set these in `api/local.settings.json`:

| Variable | Where | Purpose |
|----------|-------|---------|
| `COSMOS_CONNECTION_STRING` | local.settings.json | Cosmos DB connection |
| `AI_LANGUAGE_ENDPOINT` | local.settings.json | Azure AI Language endpoint |
| `AI_LANGUAGE_KEY` | local.settings.json | Azure AI Language key |
| `FUNCTIONS_WORKER_RUNTIME` | local.settings.json | Must be `python` |
| `AzureWebJobsStorage` | local.settings.json | Storage emulator (local dev only) |

### Azure Production (Key Vault)

Secrets are stored in Azure Key Vault (`kv-ticket-triage-g1`). The API fetches them at runtime using a service principal (IAM).

> **Why IAM instead of Managed Identity?** Azure Static Web Apps managed identity is not available on the Azure for Students free tier. We use a service principal with "Key Vault Secrets User" role as a workaround.

| Variable | Where | Purpose |
|----------|-------|---------|
| `COSMOS_CONNECTION_STRING` | Key Vault | Cosmos DB connection |
| `AI_LANGUAGE_ENDPOINT` | Key Vault | Azure AI Language endpoint |
| `AI_LANGUAGE_KEY` | Key Vault | Azure AI Language key |
| `AZURE_CLIENT_ID` | App settings | Service principal client ID |
| `AZURE_CLIENT_SECRET` | App settings | Service principal secret |
| `AZURE_TENANT_ID` | App settings | Azure AD tenant ID |
| `KEY_VAULT_URL` | App settings | Key Vault URL |

The code tries Key Vault first, falls back to environment variables for local dev.

Verify: `curl https://witty-dune-0dbfce600.7.azurestaticapps.net/api/health`

---

## Testing

Run from the project root:

```bash
python -m pytest tests -v
```

38 tests, all run without Azure credentials:

| File | Tests | Covers |
|------|-------|--------|
| `test_health.py` | 12 | Health endpoint, environment detection |
| `test_categories.py` | 9 | Categories endpoint and data structure |
| `test_tickets.py` | 17 | Combined health and categories tests |

---

## Limitations

- No real authentication — admin page uses a shared key, not sign-in
- Keyword-based classification — works for demo, needs training data for production
- No file attachments — text-only tickets
- No email notifications — status changes not communicated
- No SLA timers — no time-based escalation
- Cold starts — first request after idle can take a few seconds

---

## Future Improvements

- Azure Static Web Apps built-in authentication with admin role
- Custom Text Classification trained on real tickets
- Email notification on status change
- Setup application monitor
- File attachment support
