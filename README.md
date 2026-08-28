# TicketTriage

AI-powered helpdesk system. Students submit support tickets, Azure AI auto-categorises them, admins review and manage the queue.

## Tech Stack

- **Frontend** — Vanilla HTML/CSS/JS
- **API** — Azure Functions (Python 3.11)
- **Database** — Azure Cosmos DB (free tier)
- **AI** — Azure AI Language (F0)
- **Hosting** — Azure Static Web Apps (free plan)

## Project Structure

```
├── frontend/
│   ├── index.html          # Ticket submission form
│   ├── admin.html          # Admin dashboard
│   ├── style.css           # Styles
│   └── app.js              # UI logic
├── api/
│   ├── CreateTicket/       # POST — create ticket
│   ├── GetTickets/         # GET — list tickets
│   ├── UpdateTicketStatus/ # POST — update status
│   ├── health/             # GET — health check
│   ├── categories/         # GET — list categories
│   └── requirements.txt
├── tests/                  # 38 pytest tests
├── scripts/
│   └── seed_api.py         # Load sample data
└── architecture.svg
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tickets` | Create a new ticket |
| GET | `/api/tickets` | List all tickets |
| POST | `/api/tickets` | Update ticket status |
| GET | `/api/health` | Health check |
| GET | `/api/categories` | List categories |

## How Classification Works

Azure AI Language extracts key phrases from the ticket description, then matches them against category keywords:

- **IT Support** — wifi, password, login, laptop, network, software
- **Facilities** — aircon, toilet, light, cleaning, door, broken
- **Course Registration** — timetable, drop, enroll, class, subject
- **Student Finance** — fee, invoice, payment, scholarship, loan
- **Library Services** — book, journal, borrow, return, database

Defaults to **General Enquiry** if no match. Falls back to keyword matching if Azure AI is unavailable.

## Deployment

Runs on Azure Static Web Apps — frontend and API on the same domain, no CORS issues.

### 1. Create Resources

```bash
RG=rg-tickettriage
LOC=southeastasia
az group create -n $RG -l $LOC

# Cosmos DB (free tier)
az cosmosdb create -n cosmos-tickettriage -g $RG --enable-free-tier true
az cosmosdb sql database create -a cosmos-tickettriage -g $RG -n Helpdesk --throughput 400
az cosmosdb sql container create -a cosmos-tickettriage -g $RG -d Helpdesk -n Tickets --partition-key-path /id

# Azure AI Language (F0)
az cognitiveservices account create -n lang-tickettriage -g $RG --kind TextAnalytics --sku F0 -l $LOC --yes

# Static Web App
az staticwebapp create -n swa-tickettriage -g $RG \
  --source <your-github-url> --branch main \
  --app-location "frontend" --api-location "api" \
  --sku Free
```

### 2. Set App Settings

```bash
COSMOS_CONN=$(az cosmosdb keys list -n cosmos-tickettriage -g $RG --query primaryMasterKey -o tsv)
AI_KEY=$(az cognitiveservices account keys list -n lang-tickettriage -g $RG --query key1 -o tsv)

az staticwebapp appsettings set -n swa-tickettriage -g $RG --setting-names \
  COSMOS_CONNECTION_STRING="AccountEndpoint=https://cosmos-tickettriage.documents.azure.com:443/;AccountKey=$COSMOS_CONN;" \
  AI_LANGUAGE_ENDPOINT="https://lang-tickettriage-g1.cognitiveservices.azure.com/" \
  AI_LANGUAGE_KEY="$AI_KEY"
```

### 3. Deploy

Push to `main` — GitHub Actions runs tests and deploys automatically.

```bash
git add . && git commit -m "deploy" && git push
```

Verify: `curl https://swa-tickettriage.azurestaticapps.net/api/health`

## Testing

```bash
python -m pytest tests -v
```

38 tests covering health, categories, and ticket operations. All run without Azure credentials.

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `COSMOS_CONNECTION_STRING` | Cosmos DB connection |
| `AI_LANGUAGE_ENDPOINT` | Azure AI Language endpoint |
| `AI_LANGUAGE_KEY` | Azure AI Language key |

## Cost

All free-tier:

- **Static Web Apps** — Free plan, 100 GB/month
- **Azure Functions** — Included in free plan
- **Cosmos DB** — 1,000 RU/s + 25 GB (free tier, opt-in required)
- **Azure AI Language** — F0, 5,000 predictions/month

## Limitations

- No real authentication — admin uses a shared key
- Classification is keyword-based, not trained on real data
- No pagination on admin view
- No file attachments or email notifications
- Cold starts on first request after idle
