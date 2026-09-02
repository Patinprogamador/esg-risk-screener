# n8n workflow

A no-code mirror of the pipeline, for the portfolio's "automation" angle.

`esg-screener.workflow.json` is a starter workflow:

1. **Schedule Trigger** — every morning at 07:00
2. **HTTP Request** — `POST {{BASE_URL}}/run` (runs the pipeline on the deployed API)
3. **HTTP Request** — `GET {{BASE_URL}}/report` (fetches the Markdown briefing)
4. *(add your own)* — send step 3 to Slack / email / Notion

## Import

1. In n8n: **Workflows → Import from File** → pick `esg-screener.workflow.json`
2. Open the two HTTP Request nodes and set the URL to your deployed API base
3. Add a delivery node (Slack, Gmail, etc.) after the report step
4. Activate

The workflow calls the **same REST API** as the CLI — nothing ESG-specific lives
in n8n, it is just orchestration.
