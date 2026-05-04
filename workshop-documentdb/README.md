# Workshop 2: Build an AI Travel Agent with Azure DocumentDB

Build an autonomous AI travel agent that uses **Azure DocumentDB** as its unified memory system — handling vector search, document storage, and conversation history all in one database.

Based on the [Microsoft Learn tutorial: Build an AI travel agent with LangChain](https://learn.microsoft.com/en-us/azure/documentdb/tutorial-ai-agent).

---

## Overview

In this workshop you'll run a Python FastAPI backend that hosts an AI agent built with LangChain. The agent answers natural language travel queries by grounding its responses against real cruise data stored in Azure DocumentDB — using vector similarity search to find relevant ships, document lookups to retrieve itineraries, and writes to record bookings and persist conversation history.

The travel data is already loaded into the shared Azure DocumentDB cluster. You're here to run the agent, explore how it queries DocumentDB, and get hands-on with the vector search behavior.

**Duration:** ~10 minutes

---

## What's in the repo

```
/loader     # Data loading scripts (pre-run by facilitator — do not run again)
/api        # Python FastAPI project — this is what you'll work with
/web        # React frontend (not used in this workshop)
```

---

## Workshop Steps

### Step 1 — Start the API (2 min)

Navigate to the `/api` directory and start the FastAPI server:

```bash
python app.py
```

The server starts at `http://127.0.0.1:8000`. Open the interactive API docs in your browser:

```
http://127.0.0.1:8000/docs
```

**Get a session ID** — the agent uses this to track your conversation history in DocumentDB.

1. Expand the **`GET /session/`** endpoint
2. Click **Try it out** → **Execute**
3. Copy the session ID from the response — you'll use it in the next step

**Send your first message** to the agent:

1. Expand **`POST /agent/agent_chat`** → **Try it out**
2. Use this request body, substituting your session ID:

```json
{
  "input": "I want to take a relaxing vacation.",
  "session_id": "<your-session-id>"
}
```

3. Click **Execute** and observe the response — the agent returns cruise recommendations sourced from a **vector similarity search** against the `ships` collection in DocumentDB.

---

### Step 2 — Inspect what DocumentDB is doing (5 min)

Open the `/api` directory in your editor and find the agent tools — look in the `service/` folder (or equivalent). You're looking for three tools:

| Tool | What it does |
|---|---|
| `vacation_lookup` | Runs a **vector similarity search** against the `ships` collection to find relevant cruises |
| `itinerary_lookup` | Retrieves cruise package details and schedules for a specific ship |
| `book_cruise` | Writes a booking document to DocumentDB and validates passenger info |

**Trigger all three tools** by continuing the conversation in Swagger. Use the same session ID and send:

```json
{
  "input": "Book me a cruise on the [ship name from previous response] for 2 passengers.",
  "session_id": "<your-session-id>"
}
```

Notice that:
- The agent uses **`itinerary_lookup`** to find available packages for that ship
- It uses **`book_cruise`** to write a booking record back to DocumentDB
- Your **conversation history** from both turns is automatically stored in the `travel.history` collection — the agent remembers what you said in step 1

This is Azure DocumentDB acting as the agent's complete memory layer: vector store, document store, and session store in one place.

---

### Step 3 — Challenge: Tune the vector search threshold (2 min)

Find the `vacation_lookup` tool in the code. Locate the vector similarity search call — it filters results by a `score` threshold (something like `score >= 0.75`).

Try adjusting this value:

- **Raise it** (e.g. `0.90`) — the agent becomes more selective; it may return fewer or no results for vague queries
- **Lower it** (e.g. `0.50`) — the agent casts a wider net; results may be less relevant

Re-run the same *"I want a relaxing vacation"* query after each change and compare the recommendations. This makes the DocumentDB vector search behavior directly observable.

---

### Step 4 - Reflect (1 min)

| What you did | Azure DocumentDB capability |
|---|---|
| Agent returned cruise recommendations from a natural language query | **Vector search** — semantic similarity over embeddings |
| Agent retrieved itinerary details for a specific ship | **Document store** — structured document reads |
| Agent wrote a booking record | **Document store** — document writes |
| Second message remembered the first | **Session-based conversation history** — persisted in DocumentDB |

Azure DocumentDB handled all four of these without any additional infrastructure.

---

## 🎟️ Congratulations!

Collect your ticket and present it at the prize booth for some swag!
