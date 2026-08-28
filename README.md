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

### Recreate Resources (if needed)

```bash
RG=rg-ticket-triage

az staticwebapp create -n swa-ticket-triage -g $RG \
  --source https://github.com/kerjing0328/ticket-triage-g1.git \
  --branch main \
  --app-location "frontend" --api-location "api" \
  --sku Free --location eastasia

az staticwebapp appsettings set -n swa-ticket-triage -g $RG --setting-names \
  COSMOS_CONNECTION_STRING="<connection-string>" \
  AI_LANGUAGE_ENDPOINT="https://language-ticket-triage-g1.cognitiveservices.azure.com/" \
  AI_LANGUAGE_KEY="<key>"
```

---

## Environment Variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `COSMOS_CONNECTION_STRING` | local.settings.json / Azure app settings | Cosmos DB connection |
| `AI_LANGUAGE_ENDPOINT` | local.settings.json / Azure app settings | Azure AI Language endpoint |
| `AI_LANGUAGE_KEY` | local.settings.json / Azure app settings | Azure AI Language key |
| `FUNCTIONS_WORKER_RUNTIME` | local.settings.json | Must be `python` |
| `AzureWebJobsStorage` | local.settings.json | Storage emulator (local dev only) |

Verify configuration: `curl https://witty-dune-0dbfce600.7.azurestaticapps.net/api/health`

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
- No pagination — admin view fetches all tickets
- No file attachments — text-only tickets
- No email notifications — status changes not communicated
- No SLA timers — no time-based escalation
- Cold starts — first request after idle can take a few seconds

---

## Future Improvements

- Azure Static Web Apps built-in authentication with admin role
- Custom Text Classification trained on real tickets
- Pagination and CSV export on admin view
- Email notification on status change
- Setup application monitor
- File attachment support
