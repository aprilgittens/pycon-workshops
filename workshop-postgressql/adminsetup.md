# ShopEasy Customer Support Agent
### A 10-Minute Lab — Azure AI Foundry · PostgreSQL · RAG

This project is a working customer-support AI agent that demonstrates how to
combine **SQL queries against Azure PostgreSQL** with **Retrieval-Augmented
Generation (RAG) via Azure AI Search** using the **Microsoft Agent Framework**.

---

## What the Agent Does

When a customer asks about returning an order the agent automatically:

1. **Calls `lookup_order`** — runs a parameterized SQL query against Azure
   PostgreSQL to fetch the order date and product category.
2. **Calls `fetch_return_policy`** — embeds the category name and runs a
   hybrid (keyword + vector) search against Azure AI Search to pull the
   relevant policy chunks.
3. **Synthesizes** both results into a clear, empathetic reply that tells
   the customer whether their order is within the return window and exactly
   what to do next.

```
You: Can I return order ORD-007?

─────────────────────────────────────────────────────────────
  [TOOL] lookup_order  →  SQL query
─────────────────────────────────────────────────────────────
  Query : SELECT order_date, product_category, ...
          FROM orders JOIN customers
          WHERE order_id = 'ORD-007'
  Result: { "order_id": "ORD-007", "product_category": "Electronics",
            "order_date": "2025-04-22", "status": "Delivered", ... }
─────────────────────────────────────────────────────────────

─────────────────────────────────────────────────────────────
  [TOOL] fetch_return_policy  →  RAG / vector search
─────────────────────────────────────────────────────────────
  Index : return-policies
  Query : 'Electronics return policy refund'
  Mode  : hybrid (keyword + vector embedding)
  Found : 3 chunk(s) retrieved
─────────────────────────────────────────────────────────────

Agent: Great news! Your order ORD-007 (Dell XPS 15 Laptop) was delivered on
April 22, 2025 — that's 15 days ago, well within the 30-day return window
for Electronics. Here's what you need to do: ...
```

---

## Project Structure

```
pycon-postgres-workshop/
├── policies/
│   └── electronics_return_policy.md   ← source policy document
├── setup/
│   ├── seed_db.py                     ← creates DB schema + fake orders
│   └── create_index.py               ← creates AI Search index + uploads chunks
├── tools.py                           ← SQL tool + RAG tool (the interesting bit)
├── agent.py                           ← agent definition & system prompt
├── chat.py                            ← terminal chat entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## Part 1 — Azure Setup (done in advance by the lab facilitator)

### Prerequisites

- An **Azure subscription** with Owner or Contributor access
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed
- Python 3.10+

---

### Step 1 — Create an Azure Resource Group

```bash
az login
az group create --name rg-shopeasy-lab --location eastus2
```

---

### Step 2 — Provision Azure PostgreSQL Flexible Server

In the [Azure Portal](https://portal.azure.com) or via CLI:

```bash
az postgres flexible-server create \
  --resource-group rg-shopeasy-lab \
  --name shopeasy-pg \
  --location eastus2 \
  --admin-user pgadmin \
  --admin-password "<choose-a-strong-password>" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 16 \
  --public-access 0.0.0.0
```

Then create the database:

```bash
az postgres flexible-server db create \
  --resource-group rg-shopeasy-lab \
  --server-name shopeasy-pg \
  --database-name shopease
```

> **Firewall:** if you get connection errors, add your IP:
> ```bash
> az postgres flexible-server firewall-rule create \
>   --resource-group rg-shopeasy-lab \
>   --name shopeasy-pg \
>   --rule-name AllowMyIP \
>   --start-ip-address <your-ip> \
>   --end-ip-address <your-ip>
> ```

---

### Step 3 — Provision Azure AI Search

```bash
az search service create \
  --resource-group rg-shopeasy-lab \
  --name shopeasy-search \
  --location eastus2 \
  --sku basic
```

Retrieve the admin API key (you will need it for `.env`):

```bash
az search admin-key show \
  --resource-group rg-shopeasy-lab \
  --service-name shopeasy-search \
  --query primaryKey -o tsv
```

---

### Step 4 — Provision Azure OpenAI (for embeddings)

1. In the [Azure Portal](https://portal.azure.com), search for **Azure OpenAI**.
2. Create a new resource in `rg-shopeasy-lab` (region: `East US 2` or `Sweden Central`).
3. Once deployed, go to **Azure OpenAI Studio** → **Deployments** → **Deploy model**.
4. Deploy **`text-embedding-ada-002`** with deployment name `text-embedding-ada-002`.
5. Copy the **endpoint** and **API key** from the resource's *Keys and Endpoint* blade.

---

### Step 5 — Create an Azure AI Foundry Project

1. Go to [ai.azure.com](https://ai.azure.com) and sign in.
2. Click **+ New project**.
3. Create a **new hub** (or use an existing one) linked to the same subscription.
4. Name the project `shopeasy-lab`.
5. In the project, go to **Models + endpoints** → **Deploy model** →
   select **`gpt-4o`** and deploy it. Note the deployment name (e.g. `gpt-4o`).
6. From the project **Overview** page, copy the **Project endpoint**
   (format: `https://<hub>.services.ai.azure.com/api/projects/<project>`).

#### Grant yourself the Contributor role on the Foundry project

The agent uses `DefaultAzureCredential` (your `az login` identity). Make sure
your Azure AD account has the **Azure AI Developer** or **Contributor** role on
the Foundry project resource:

```bash
# Get the resource ID of the AI hub
az resource show \
  --resource-group rg-shopeasy-lab \
  --resource-type "Microsoft.MachineLearningServices/workspaces" \
  --name <your-hub-name> \
  --query id -o tsv

# Assign the role (replace with your object ID and the resource ID above)
az role assignment create \
  --assignee "<your-azure-ad-object-id>" \
  --role "Azure AI Developer" \
  --scope "<resource-id>"
```

---

## Part 2 — Local Setup

### Step 6 — Clone & Install

```bash
git clone <this-repo>
cd pycon-postgres-workshop
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# Install in the correct order (agent-framework has a dependency pin)
pip install azure-ai-agentserver-agentframework==1.0.0b16 \
            azure-ai-agentserver-core==1.0.0b16 \
            agent-dev-cli==0.0.1b260316

pip install agent-framework-core==1.0.0rc6 \
            agent-framework-foundry==1.0.0rc6 \
            agent-framework-openai==1.0.0rc6

pip install -r requirements.txt
```

---

### Step 7 — Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in all values from the Azure resources you created:

| Variable | Where to find it |
|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | AI Foundry → Project → Overview |
| `FOUNDRY_MODEL_DEPLOYMENT_NAME` | AI Foundry → Models + endpoints |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI → Keys and Endpoint |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI → Keys and Endpoint |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Azure OpenAI Studio → Deployments |
| `AZURE_SEARCH_ENDPOINT` | Azure Portal → Search service → Overview |
| `AZURE_SEARCH_API_KEY` | Azure Portal → Search service → Keys |
| `AZURE_SEARCH_INDEX_NAME` | Leave as `return-policies` |
| `POSTGRES_HOST` | Azure Portal → PostgreSQL → Overview → Server name |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | `shopease` |
| `POSTGRES_USER` | The admin username you chose |
| `POSTGRES_PASSWORD` | The admin password you chose |

---

### Step 8 — Authenticate with Azure (for Foundry)

```bash
az login
```

This sets up `DefaultAzureCredential` used by the agent to call the Foundry model.

---

## Part 3 — Data Setup (done in advance by the lab facilitator)

### Step 9 — Seed the PostgreSQL Database

```bash
python setup/seed_db.py
```

Expected output:
```
Connecting to PostgreSQL …
Creating schema …
Seeding customers …
Seeding orders …

Done!  10 order(s) in the database.

Sample rows:
  ORD-001  2025-03-23  Electronics      Sony WH-1000XM5 Wireless Noise-Cancelling H...
  ORD-002  2025-04-27  Books            Python Crash Course, 3rd Edition
  ...
```

---

### Step 10 — Create the AI Search Index & Upload Policy Documents

```bash
python setup/create_index.py
```

Expected output:
```
Creating index 'return-policies' …
  Index ready.
Generating embeddings for 8 chunks …
  Embeddings done.
Uploading documents to the index …
  Uploaded 8/8 documents successfully.

Index contents:
  [Electronics     ]  Electronics Return Window
  [Electronics     ]  Electronics Return Eligibility Requirements
  [Electronics     ]  Electronics Refund Amounts
  [Electronics     ]  How to Return an Electronics Item
  [Electronics     ]  Electronics Warranty vs. Return Policy
  [Clothing        ]  Clothing & Apparel Return Policy
  [Books           ]  Books Return Policy
  [Home & Kitchen  ]  Home & Kitchen Return Policy
```

---

## Part 4 — Lab (10 minutes)

### Start the Agent

```bash
python chat.py
```

You will see the startup banner with a list of demo order IDs and sample questions.

---

### Exercise 1 — Watch the Full Flow (3 min)

Ask the agent about an electronics order:

```
You: Can I return order ORD-007?
```

Watch the terminal output carefully. You will see **two tool calls** happen
before the agent writes its answer:

1. **`[TOOL] lookup_order → SQL query`**
   - The query printed is parameterized (`WHERE order_id = $1`) — no SQL injection risk.
   - The result JSON shows the `order_date` and `product_category`.

2. **`[TOOL] fetch_return_policy → RAG / vector search`**
   - The search query is formed from the category name (`Electronics return policy refund`).
   - The index is searched with *hybrid* mode: both keyword BM25 and vector cosine similarity.
   - 3 policy chunks are returned and passed to the model.

3. **The agent's final response** synthesizes both pieces of information.

---

### Exercise 2 — Test the Return Window Logic (2 min)

Try an order that is **outside** the 30-day electronics window:

```
You: I want to return order ORD-001.
```

`ORD-001` was delivered 45 days ago. Notice how the agent correctly says
the order is outside the return window — it computed this from the `order_date`
returned by the SQL query and the window stated in the policy document.

Then try an order **within** the window:

```
You: What about order ORD-006?
```

`ORD-006` (AirPods Pro) was delivered 8 days ago — well within 30 days.

---

### Exercise 3 — Explore the Code (3 min)

Open **`tools.py`** and look at two functions:

**`lookup_order`** (line ~60)
```python
row = await _pool.fetchrow(
    """
    SELECT o.order_id, o.order_date, o.product_name, o.product_category, ...
    FROM   orders o
    JOIN   customers c ON o.customer_id = c.customer_id
    WHERE  o.order_id = $1   ← parameterized, safe from SQL injection
    """,
    oid,
)
```
The `$1` placeholder is the asyncpg parameterized query syntax.
`asyncpg` sends the query and the parameter separately — the database engine
never sees them concatenated, making SQL injection impossible.

**`fetch_return_policy`** (line ~115)
```python
embedding = await _embed(search_text)          # 1536-dim vector via Azure OpenAI

vector_query = VectorizedQuery(
    vector=embedding,
    k_nearest_neighbors=3,
    fields="content_vector",
)

results = await search_client.search(
    search_text=search_text,                   # keyword side of hybrid search
    vector_queries=[vector_query],             # vector side
    select=["title", "content", "category"],
    top=3,
)
```
The hybrid search combines traditional keyword matching (BM25 scoring) with
vector cosine similarity. Documents whose text overlaps the query *and* whose
embedding vector is geometrically close both score well.

Open **`setup/create_index.py`** to see how the policy document was split into
chunks and uploaded with pre-computed embeddings.

---

### Exercise 4 — Try Your Own Questions (2 min)

Some ideas:

```
You: My laptop arrived broken. Order ORD-007. What can I do?
You: Is there a restocking fee if I return an opened TV?
You: I lost the box for my AirPods. Can I still return order ORD-006?
You: What orders do I have?   ← the agent will ask for an order ID
```

---

## Key Architecture Diagram

```
User Terminal
     │
     ▼
chat.py  ──── agent.run(message, stream=True) ────►  Azure AI Foundry
                                                         GPT-4o
                                                         │
                          ┌──────────────────────────────┤
                          │  Tool calls (function calling)
                          │
              ┌───────────▼────────────┐    ┌────────────────────────┐
              │     lookup_order       │    │  fetch_return_policy   │
              │   (tools.py line ~60)  │    │  (tools.py line ~115)  │
              └───────────┬────────────┘    └──────────┬─────────────┘
                          │                            │
                          ▼                            ▼
              Azure PostgreSQL                  Azure AI Search
              (orders + customers)              (return-policies index)
              asyncpg parameterized             hybrid: BM25 + vector
              SQL query                         embeddings via Azure OpenAI
```

---

## Troubleshooting

| Error | Likely cause | Fix |
|---|---|---|
| `DefaultAzureCredential: No credentials found` | Not logged in to Azure CLI | Run `az login` |
| `Connection refused` (PostgreSQL) | Firewall rule missing | Add your IP in Azure Portal → PostgreSQL → Networking |
| `Index not found` (AI Search) | Setup script not run | Run `python setup/create_index.py` |
| `Table "orders" does not exist` | DB not seeded | Run `python setup/seed_db.py` |
| `404 model not found` | Wrong deployment name | Check `FOUNDRY_MODEL_DEPLOYMENT_NAME` in `.env` |
| `asyncpg.exceptions.InvalidPasswordError` | Wrong DB credentials | Double-check `POSTGRES_USER` / `POSTGRES_PASSWORD` in `.env` |

---

## Python & SDK Versions

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| agent-framework-core | 1.0.0rc6 |
| agent-framework-foundry | 1.0.0rc6 |
| azure-ai-agentserver-* | 1.0.0b16 |
| azure-search-documents | 11.6.0b4 |
| asyncpg | 0.29.0 |
| openai | 1.35.0 |

> The Microsoft Agent Framework is in preview.  Version pins matter — see the
> install note in `requirements.txt`.
