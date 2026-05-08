# Customer Support Agent with Microsoft Foundry, Microsoft Agent Framework, Azure PostgreSQL & Azure AI Search

Query a PostgreSQL database and a vector search index in real time, then explore the code behind the SQL queries and hybrid RAG search that power an AI agent's responses.

---

## Start the Agent (30 seconds)

Launch the agent from your terminal to start an interactive customer support session.

In the terminal, run the command `python lab-postgressql/chat.py`

You will see the startup banner with a list of demo order IDs and sample questions.

## Watch the Full Flow (2 min)

See both tools fire in sequence as the agent resolves a real support request (a SQL lookup followed by a vector search) before synthesizing a final answer.

Ask the agent about an electronics order:

```
You: Can I return order ORD-007?
```

Watch the terminal output carefully. You will see **two tool calls** happen
before the agent writes its answer:

1. `[TOOL] lookup_order → SQL query`
   - The query printed is parameterized (`WHERE order_id = $1`) — no SQL injection risk.
   - The result JSON shows the `order_date` and `product_category`.

2. `[TOOL] fetch_return_policy → RAG / vector search`
   - The search query is formed from the category name (`Electronics return policy refund`).
   - The index is searched with *hybrid* mode: both keyword BM25 and vector cosine similarity.
   - 3 policy chunks are returned and passed to the model.

3. The agent's final response synthesizes both pieces of information.

---

## Test the Return Window Logic (2 min)

Put the date-window logic to the test by trying orders on both sides of the 30-day return cutoff. The agent computes eligibility at runtime from live data, not hardcoded rules.

1. Try an order that is **outside** the 30-day electronics window:

    ```
    You: I want to return order ORD-001.
    ```

    `ORD-001` was delivered more than days ago. Notice how the agent correctly says
    the order is outside the return window. It computed this from the `order_date`
    returned by the SQL query and the window stated in the policy document.

1. Try an order **within** the 30-day window:

    ```
    You: What about order ORD-006?
    ```

    `ORD-006` (AirPods Pro) was delivered 8 days ago, well within 30 days.

---

## Explore the Code (3 min)

Dig into the two tool functions that power the agent's data access and see exactly how parameterized queries and hybrid vector search are implemented.

1. Open `tools.py` and look at two functions:

    `lookup_order` (line ~71)
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
    `asyncpg` sends the query and the parameter separately. the database engine
    never sees them concatenated, making SQL injection impossible.

1. `fetch_return_policy` (line ~136)
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

1. Open `setup/create_index.py` to see how the policy document was split into
chunks and uploaded with pre-computed embeddings.

---

## Try Your Own Questions (2.5 min)

Go off-script and see how the agent handles edge cases and variations it wasn't explicitly tested for. Each response is still grounded in live data from PostgreSQL and Azure AI Search.

> 💡 **Order IDs:** All demo orders (ORD-001 through ORD-010) are defined in `setup/seed_db.py` if you want to browse products, categories, and delivery dates before chatting.

Some ideas:

- My laptop arrived broken. Order ORD-007. What can I do?
- Is there a restocking fee if I return an opened TV?
- I lost the box for my AirPods. Can I still return order ORD-006?
- What orders do I have? (**Note**: the agent will ask for an Order ID)

---

## Reflection

Take a moment to connect what you just did to the services that made it possible.

- **Parameterized SQL queries** — the agent looked up order details safely using `$1` placeholders, keeping user input and query logic completely separate to prevent SQL injection
- **Hybrid RAG search** — the agent retrieved the right return policy by combining keyword matching (BM25) and vector cosine similarity against pre-computed embeddings in Azure AI Search
- **Tool orchestration** — the agent decided on its own which tools to call and in what order, then synthesized both results into a single, coherent answer
- **Policy as a knowledge base** — instead of hardcoding business rules, the agent retrieved policy chunks at runtime, meaning the policy can be updated without changing any agent code

Together, Azure PostgreSQL and Azure AI Search gave the agent grounded, real-time access to structured data and unstructured documents — no hallucinated return windowso or hardcoded rules.

---

## 🎟️ Congratulations!

Collect your ticket and present it at the prize booth for some swag!

