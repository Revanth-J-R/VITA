# n8n Workflow Setup for VITA

VITA uses **n8n** for downstream automation: every triage result is sent to n8n
which can fire emergency alerts, log sessions, and connect to any external service.

---

## Prerequisites

- Node.js 18+ installed
- VITA backend running at `http://localhost:8000`

---

## 1. Install & Start n8n

```powershell
npx n8n
```

n8n will open at **http://localhost:5678**

---

## 2. Import the VITA Workflow

1. Open n8n at `http://localhost:5678`
2. Click **"+"** to create a new workflow
3. Click the **⋮ menu** (top right) → **Import from File**
4. Select `n8n/vita_workflow.json` from this project
5. Click **Activate** (toggle in top right)

---

## 3. Get the Webhook URL

After activating, click the **VITA Webhook** node. Copy the **Production URL**, which looks like:

```
http://localhost:5678/webhook/vita-triage
```

---

## 4. Configure VITA

Create a `.env` file in the VITA root (copy from `.env.example`):

```powershell
Copy-Item .env.example .env
```

Edit `.env` and paste your webhook URL:

```
N8N_WEBHOOK_URL=http://localhost:5678/webhook/vita-triage
```

Restart the VITA server:

```powershell
.\venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 5. Verify

Open VITA at `http://localhost:8000`, analyze any symptom. Then check:

- n8n → **Executions** tab → you should see a successful execution
- For emergency symptoms (e.g. "chest pain and difficulty breathing"), the **Emergency Alert** branch will fire

---

## Workflow Nodes

| Node | Description |
|---|---|
| **VITA Webhook** | Receives triage JSON from FastAPI |
| **Is Emergency?** | Routes based on `is_emergency` field |
| **Send Emergency Alert** | Console logs emergency (replace with Email/Slack/SMS) |
| **Log Triage Result** | Console logs all triage events (replace with Google Sheets/DB) |
| **Respond to VITA** | Returns `{"received": true}` to FastAPI |

---

## Adding Real Alerts

To send a real email or Slack message on emergency:
1. Click the **Send Emergency Alert** node → Delete it
2. Add an **Email** or **Slack** node in its place
3. Map `{{ $json.emergency_message }}` and `{{ $json.original_input }}` into the message
