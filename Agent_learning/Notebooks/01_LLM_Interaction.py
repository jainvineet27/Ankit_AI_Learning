# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
from openai import OpenAI
import os

# How to get your Databricks token: https://docs.databricks.com/en/dev-tools/auth/pat.html
# DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN')
# Alternatively in a Databricks notebook you can use this:
DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

client = OpenAI(
    api_key=DATABRICKS_TOKEN,
    base_url="https://dbc-bc8edf8f-7367.cloud.databricks.com/serving-endpoints"
)

response = client.chat.completions.create(
    model="databricks-gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "tell me use cse of mcp iwth databricks "
        }
    ],
    max_tokens=5000
)

#print(response.choices[0].message.content)

# COMMAND ----------

print(response.choices[0].message.content[1].get("text"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Databricks Lakehouse + Microsoft Fabric Agent  
# MAGIC *(What it is, why it matters, how it works, and how to get started)*  
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 1. The two pieces in a nutshell  
# MAGIC
# MAGIC | Component | Core purpose | Where it lives | Key technologies |
# MAGIC |-----------|--------------|----------------|------------------|
# MAGIC | **Databricks Lakehouse** | A unified analytics platform that merges the low‑cost scalability of a data lake with the ACID‑transactional guarantees and performance of a data warehouse. | Azure Databricks (or AWS/GCP Databricks) – managed Spark service built on Delta Lake. | Apache Spark, Delta Lake, Unity Catalog, Photon (SQL engine), MLflow, Delta Sharing, etc. |
# MAGIC | **Microsoft Fabric Agent** (formerly *Fabric Connector for Databricks*) | A lightweight runtime that enables Microsoft Fabric workspaces (Lakehouse, Data Engineering, Data Science, Power BI, etc.) to securely discover, query, and move data stored in an external Databricks Lakehouse. | Runs as a managed service inside the Fabric control plane (no customer‑installed VM or container). | OAuth / Azure AD, Service Principal auth, Spark‑SQL endpoint, Delta Lake protocol, REST/ODBC/JDBC drivers. |
# MAGIC
# MAGIC Together they let you treat an existing Databricks Delta Lake as a **first‑class Fabric Lakehouse** – you can build Fabric notebooks, pipelines, and Power BI reports that read/write the same Delta tables that your Spark jobs already use, without data duplication.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 2. Why you’d want the Fabric → Databricks integration  
# MAGIC
# MAGIC | Business driver | What the integration delivers |
# MAGIC |-----------------|--------------------------------|
# MAGIC | **Single source of truth** | All downstream analytics (Fabric notebooks, Power BI datasets) see the same Delta tables that production pipelines write in Databricks. |
# MAGIC | **Cost‑effective scaling** | Leverage Databricks’ auto‑scaling Spark clusters for heavy transformations, while using Fabric’s low‑cost SQL engine for ad‑hoc analytics. |
# MAGIC | **Governance & security** | Azure AD‑based access is enforced end‑to‑end. Unity Catalog permissions are respected when Fabric queries Delta tables. |
# MAGIC | **Developer productivity** | Data engineers stay in Databricks notebooks; data analysts stay in Fabric notebooks/Power BI – both share the same metadata (catalog, schema). |
# MAGIC | **Reduced data movement** | No ETL copies to a separate Fabric Lakehouse; the Fabric agent streams directly over the Delta log. |
# MAGIC | **Hybrid workloads** | Run batch ETL in Databricks, real‑time dashboards in Fabric, and ML models in Databricks – all on the same underlying delta tables. |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 3. High‑level architecture  
# MAGIC
# MAGIC ```
# MAGIC +-------------------+      OAuth/Managed Identity       +-------------------+
# MAGIC |   Microsoft       |  <----------------------------->  |   Azure Databricks |
# MAGIC |   Fabric          |                                  |   (Delta Lake)    |
# MAGIC |   Workspace       |   Fabric Agent (service)          |   (Photon/SQL)    |
# MAGIC +-------------------+                                   +-------------------+
# MAGIC         ^   ^                                                    ^
# MAGIC         |   |   SQL/ODBC/JDBC calls (push‑down)                  |
# MAGIC         |   +-------------------+------------------------------+
# MAGIC         |                       |
# MAGIC         |   Fabric UI (Lakehouse, notebooks, Power BI)
# MAGIC         |
# MAGIC         +--- Fabric Data Factory pipelines (optional)
# MAGIC ```
# MAGIC
# MAGIC * The **Fabric Agent** is a managed micro‑service that authenticates to Azure AD, obtains a token for the target Databricks workspace, and opens a **JDBC/ODBC** connection to the Databricks SQL endpoint (or directly to the Delta log via the Delta Sharing protocol).  
# MAGIC * All **SQL push‑down** (filters, aggregates, joins) is executed by Databricks’ Photon engine, so Fabric only streams the result set.  
# MAGIC * **Metadata** (catalog, schema, table properties) is fetched from **Unity Catalog** (or the legacy Hive metastore) and exposed inside the Fabric Lakehouse UI, making the external tables appear as native Fabric objects.  
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 4. How the Fabric Agent authenticates  
# MAGIC
# MAGIC | Method | When you’d use it | Setup steps |
# MAGIC |--------|-------------------|-------------|
# MAGIC | **Managed Identity** (recommended) | Fabric workspace is in the same Azure AD tenant as the Databricks workspace. | 1. Enable a system‑assigned managed identity for the Fabric workspace.<br>2. Grant that identity the **`databricks.sql.access`** role (or a custom role) on the Databricks SQL endpoint.<br>3. Add the identity to the Unity Catalog ACL for the desired catalog/tables. |
# MAGIC | **Service Principal** | Cross‑tenant scenario or you need a dedicated identity. | 1. Create an Azure AD app registration.<br>2. Add the app as a service principal to Databricks (via the Admin console or SCIM API).<br>3. Assign the required Databricks SQL role and Unity Catalog permissions.<br>4. Store the client‑id/secret or certificate in Fabric’s **Key Vault** and reference it in the connection config. |
# MAGIC | **User‑delegated OAuth** | Users directly query Databricks and you want row‑level security enforced by user tokens. | 1. Register an Azure AD application that supports **`openid`**, **`profile`**, **`offline_access`** and **`https://databricks.azure.com/sql`** scopes.<br>2. Enable **user‑impersonation** on the Databricks SQL endpoint.<br>3. Fabric UI will prompt the user to sign‑in the first time, then cache the token. |
# MAGIC
# MAGIC All three approaches use **Azure AD token‑exchange**, so no passwords or long‑lived secrets travel to the Fabric runtime.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 5. Step‑by‑step: Connecting a Fabric Lakehouse to a Databricks Lakehouse  
# MAGIC
# MAGIC > **Assumption:** You already have a Databricks workspace with a Unity Catalog and at least one Delta table (`sales.sales_fact`).  
# MAGIC
# MAGIC | # | Action | Details |
# MAGIC |---|--------|---------|
# MAGIC | 1 | **Create a Databricks SQL endpoint** | In the Databricks console → SQL Warehouses → *Create SQL warehouse*. Choose Photon, set auto‑scale, and note the **Warehouse ID** (used as the server name). |
# MAGIC | 2 | **Configure Unity Catalog permissions** | Grant the Fabric identity (managed identity or SP) `SELECT` on the catalog/database, and optionally `INSERT/UPDATE` if you need writeback. |
# MAGIC | 3 | **Enable the Fabric connector** | In Power BI Service → Settings → *Admin portal* → *External connections* → enable **Databricks**. (In Fabric UI it’s under *Lakehouse → External sources → Add new source*). |
# MAGIC | 4 | **Add a new external connection** | In the Fabric workspace: <br>1. Go to **Lakehouse → Manage → External tables**.<br>2. Click **Add external source** → **Databricks**.<br>3. Fill in: <br>   • Server: `<warehouse-id>.sql.azuredatabricks.net`<br>   • Authentication: Managed Identity / Service Principal (pick the one you set up).<br>   • Catalog: `unity_catalog_name` |
# MAGIC | 5 | **Import tables** | After validation, Fabric will list all tables you have permission on. Select `sales.sales_fact` (or the whole database) and click **Import**. Fabric creates **linked tables** that point back to the Delta files. |
# MAGIC | 6 | **Start querying** | Open a Fabric notebook (Spark Python or SQL) or Power BI and run: <br>```sql SELECT * FROM sales.sales_fact WHERE order_date > '2024-01-01'``` <br>Behind the scenes the query is sent via the Fabric Agent to the Databricks SQL warehouse; Photon executes the heavy lifting. |
# MAGIC | 7 | **Write‑back (optional)** | To enable inserts/updates, set the linked table’s **write mode** to *Direct* (instead of *Staging*). Fabric will issue Delta `MERGE` statements that are executed by Databricks, preserving ACID guarantees. |
# MAGIC | 8 | **Refresh metadata** | Whenever a new Delta table is added in Databricks, run **Refresh external tables** in Fabric to sync the catalog. |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 6. Data‑flow & performance considerations  
# MAGIC
# MAGIC | Aspect | What to watch for | Recommended practice |
# MAGIC |--------|-------------------|----------------------|
# MAGIC | **Query push‑down** | Only predicates that Databricks SQL can understand are pushed down. Complex UDFs defined in Fabric will be evaluated locally, causing data transfer. | Keep transformations in SQL; if you need Python UDFs, run them in Databricks notebooks and expose the result as a new Delta table. |
# MAGIC | **Network latency** | Fabric queries travel over Azure backbone to the Databricks SQL endpoint. Latency is usually < 30 ms intra‑region, higher across regions. | Keep Fabric and Databricks in the **same Azure region**; otherwise use **Azure Private Link** to avoid internet hops. |
# MAGIC | **Concurrency limits** | Databricks SQL warehouses have a maximum number of concurrent queries (depends on size). Fabric can generate many short queries from Power BI visuals. | Size the warehouse appropriately (e.g., *Large* for heavy BI load) and enable **auto‑scale**; monitor `active_queries` via Databricks monitoring. |
# MAGIC | **Caching** | Fabric does **no caching** of results – each visual request hits Databricks. | Enable **Result Cache** in Databricks SQL (`SET enable_result_cache = true;`) or materialize hot tables as pre‑aggregated Delta tables. |
# MAGIC | **Write throughput** | Writes are performed by Databricks via `INSERT`/`MERGE`. High write volume can cause write conflicts on the same partitions. | Partition tables wisely (e.g., by date) and use **optimistic concurrency control** (Delta’s default) – Fabric will surface any conflict as a retryable error. |
# MAGIC | **Security audit** | All access is logged both in Fabric (Activity Log) and Databricks (SQL Warehouse audit). | Centralize logs in Azure Monitor or Sentinel for compliance. Enable **Data Loss Prevention** policies in Fabric if needed. |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 7. Where the integration shines – typical use cases  
# MAGIC
# MAGIC | Use case | How you implement it | Benefits |
# MAGIC |----------|---------------------|----------|
# MAGIC | **Self‑service BI on production data** | Power BI reports connect directly to Databricks tables via the Fabric agent. | No ETL copies → freshest data + governed access. |
# MAGIC | **Hybrid batch‑/real‑time pipelines** | Batch ETL runs nightly in Databricks (Spark). Near‑real‑time dashboards in Fabric query the same tables for the latest partitions. | Consistent metrics, reduced latency. |
# MAGIC | **Data‑science hand‑off** | Data scientists train models on Delta tables in Databricks. Business analysts explore model predictions in Fabric notebooks and embed results in Power BI. | Single source of truth, smoother collaboration. |
# MAGIC | **Multi‑cloud data federation** | If you have a Databricks workspace on AWS but Fabric in Azure, use **Private Link + Azure ExpressRoute** to connect securely. | Leverages best‑of‑both clouds without data duplication. |
# MAGIC | **Regulated environments** | Unity Catalog enforces column‑level security. Fabric respects those masks, so analysts only see allowed columns. | End‑to‑end compliance (GDPR, HIPAA). |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 8. Limitations & gotchas  
# MAGIC
# MAGIC | Limitation | Work‑around / Mitigation |
# MAGIC |------------|--------------------------|
# MAGIC | **No direct file‑system access** – Fabric cannot query raw Parquet files stored in ADLS without a Databricks endpoint. | Either expose the files via **Delta Sharing** (still requires a server) or ingest them into a Databricks Delta table first. |
# MAGIC | **Spark‑specific functions** (e.g., `approx_percentile`, `array_union`) are not available in Databricks SQL. Queries using them will fail when run from Fabric. | Rewrite using standard SQL equivalents or move the logic into a Databricks notebook and materialize the result. |
# MAGIC | **Schema evolution restrictions** – Adding a column in Databricks updates the Delta schema but Fabric linked tables may need a manual **Refresh** to see the new column. | Automate a nightly pipeline that runs `REFRESH EXTERNAL TABLES` in Fabric. |
# MAGIC | **Write‑back latency** – Inserts go through the Databricks SQL engine, which can be slower than bulk loading via `COPY INTO`. | For bulk loads, stage data in ADLS and run a Databricks notebook to `COPY INTO` the target Delta table. |
# MAGIC | **Cost separation** – You pay for both Fabric compute (for notebooks/Power BI) and Databricks SQL warehouse. | Right‑size the SQL warehouse (auto‑scale) and use Fabric’s **serverless** tier for low‑volume queries. |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 9. Operational monitoring  
# MAGIC
# MAGIC | Tool | What you monitor | Typical alerts |
# MAGIC |------|------------------|----------------|
# MAGIC | **Azure Monitor – Databricks metrics** | `SQLWarehouse.ActiveQueries`, `CPUUtilization`, `CacheHitRate`. | > 80 % CPU, query latency > 5 s, high cache miss. |
# MAGIC | **Fabric Activity Log** | `ExternalConnectionSuccess`, `ExternalConnectionFailure`, `DataWrite` events. | Repeated auth failures → token expiry; write errors → delta‑conflict. |
# MAGIC | **Databricks Workspace Logs** | Audit logs for `SELECT`, `INSERT`, `MERGE` executed via the Fabric agent. | Unexpected table access → security investigation. |
# MAGIC | **Power BI Usage Metrics** | Dataset refresh duration, query cost. | Sudden spikes → may indicate missing cache or warehouse scaling needed. |
# MAGIC
# MAGIC Create a **Log Analytics workspace** that aggregates both Fabric and Databricks logs; set up a **Sentinel** rule to fire on `"SELECT FROM external_table WHERE source='fabric'"` that exceeds a latency threshold.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 10. Quick cheat‑sheet (copy‑paste for your docs)
# MAGIC
# MAGIC ```yaml
# MAGIC # Fabric → Databricks connection (Managed Identity)
# MAGIC connection:
# MAGIC   type: databricks
# MAGIC   server: <warehouse-id>.sql.azuredatabricks.net
# MAGIC   authentication: managed_identity
# MAGIC   catalog: unity_catalog_name
# MAGIC   database: sales
# MAGIC   tables:
# MAGIC     - sales_fact
# MAGIC     - dim_customer
# MAGIC permissions:
# MAGIC   - databricks.sql.access   # on the SQL warehouse
# MAGIC   - unity_catalog.select   # on catalog/database
# MAGIC   - unity_catalog.write    # optional, for write‑back
# MAGIC network:
# MAGIC   private_link: true       # recommended
# MAGIC   region: eastus2
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 11. TL;DR (the 30‑second elevator pitch)
# MAGIC
# MAGIC - **Databricks Lakehouse** = Delta‑Lake + Spark + Photon = a single platform for batch, streaming, and ML on ACID‑guaranteed data.  
# MAGIC - **Microsoft Fabric Agent** = a managed connector that lets Fabric workspaces treat an external Databricks Delta Lake as a native Fabric Lakehouse.  
# MAGIC - It uses **Azure AD** for secure token‑based auth, pushes SQL work to Databricks’ Photon engine, and respects Unity Catalog permissions.  
# MAGIC - Result: analysts get **real‑time BI** on production data, data engineers keep using their existing Databricks pipelines, and both sides share a single source of truth without copying data.  
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 12. Next steps for you  
# MAGIC
# MAGIC 1. **Confirm the target region** – keep Fabric and Databricks in the same Azure region.  
# MAGIC 2. **Choose the auth model** (Managed Identity is the simplest if the tenant matches).  
# MAGIC 3. **Provision a Databricks SQL warehouse** sized for your expected BI concurrency.  
# MAGIC 4. **Create the external connection** in Fabric (follow the step‑by‑step table above).  
# MAGIC 5. **Run a pilot report** in Power BI or a Fabric notebook; monitor latency and adjust the warehouse size.  
# MAGIC 6. **Set up automated metadata refresh** (e.g., a daily Fabric pipeline that runs `REFRESH EXTERNAL TABLES`).  
# MAGIC
# MAGIC If you hit any specific error (authentication, schema sync, query latency), let me know the exact message and I can walk you through the troubleshooting steps. Happy lake‑house building!

# COMMAND ----------

# MAGIC %md
# MAGIC AI agents are gaining popularity because they:
# MAGIC
# MAGIC - **Automate complex tasks** — handle scheduling, data analysis, and customer support without constant human oversight.  
# MAGIC - **Boost productivity** — integrate with tools (email, calendars, APIs) to streamline workflows.  
# MAGIC - **Offer personalization** — adapt responses to user preferences and context.  
# MAGIC - **Scale knowledge** — leverage large language models to provide up‑to‑date information across domains.  
# MAGIC - **Lower entry barriers** — user‑friendly interfaces let non‑technical people deploy powerful automation.  
# MAGIC - **Drive innovation** — enable new services (e.g., autonomous agents, digital assistants) that were previously impractical.

# COMMAND ----------

# MAGIC %sql
# MAGIC select ai_query('databricks-gpt-oss-120b','why are ai agents gettin =g popular')

# COMMAND ----------

# MAGIC %md
# MAGIC **Why AI agents are becoming so popular**
# MAGIC
# MAGIC 1. **Rapid advances in core technology**  
# MAGIC    - **Large language models (LLMs)** such as GPT‑4, Claude, LLaMA 2 can understand and generate human‑like text, making agents far more capable than earlier rule‑based bots.  
# MAGIC    - **Multimodal models** (text + image + audio) let agents perceive and act across many data types.  
# MAGIC    - **Reinforcement‑learning‑from‑human‑feedback (RLHF)** and fine‑tuning improve safety, alignment, and task‑specific performance.
# MAGIC
# MAGIC 2. **Massively increased compute & data**  
# MAGIC    - Cloud providers now offer cheap, on‑demand GPU/TPU clusters, lowering the barrier to train or run sophisticated agents.  
# MAGIC    - Public datasets (web text, code, images, conversational logs) give models the breadth needed for general‑purpose reasoning.
# MAGIC
# MAGIC 3. **Clear business value**  
# MAGIC    - **Automation of repetitive tasks** (customer support, scheduling, data entry) cuts labor costs and speeds response times.  
# MAGIC    - **Decision‑support** (drafting contracts, code generation, market analysis) augments human expertise, increasing productivity.  
# MAGIC    - **Personalization**: agents can tailor recommendations, tutoring, or health advice to individual users, driving higher engagement and satisfaction.
# MAGIC
# MAGIC 4. **Ease of integration**  
# MAGIC    - **APIs and SDKs** (OpenAI, Anthropic, Cohere, Azure AI) let developers embed agents in apps, websites, and internal tools with just a few lines of code.  
# MAGIC    - **Tool‑use extensions** (retrieval‑augmented generation, code execution, web browsing) enable agents to fetch up‑to‑date information or perform actions beyond pure language generation.
# MAGIC
# MAGIC 5. **User‑centric experiences**  
# MAGIC    - Conversational interfaces feel natural; people can “talk” to software instead of learning complex UIs.  
# MAGIC    - Voice assistants (Alexa, Siri, Google Assistant) have familiarized the public with AI‑driven interaction, paving the way for more capable agents.
# MAGIC
# MAGIC 6. **Open‑source momentum**  
# MAGIC    - Projects like **LangChain**, **AutoGPT**, **Agentic‑LLM** frameworks provide reusable building blocks for creating autonomous agents.  
# MAGIC    - Community‑driven models (e.g., LLaMA 2, Mistral) lower cost and encourage experimentation, accelerating adoption.
# MAGIC
# MAGIC 7. **Regulatory and ethical focus**  
# MAGIC    - Growing standards for transparency, data privacy, and AI safety give enterprises confidence to deploy agents responsibly, reducing earlier legal hesitations.
# MAGIC
# MAGIC 8. **Cultural hype & media coverage**  
# MAGIC    - High‑profile demos (ChatGPT, DALL·E, GitHub Copilot) showcase tangible capabilities, sparking curiosity among developers, investors, and the general public.  
# MAGIC    - Venture capital funding has surged, creating a feedback loop of research, productization, and publicity.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Bottom line
# MAGIC AI agents are popular because the **technology has finally caught up with real‑world needs**: they’re more capable, cheaper to run, easy to integrate, and deliver measurable business and user benefits. The combination of technical breakthroughs, ecosystem support, and market demand creates a virtuous cycle that continues to drive rapid adoption.