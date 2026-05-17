# BOLDR Intelligence Loop Workflow

**Workflow ID:** `GDH4I878uz44yXDC`
**n8n URL:** http://192.168.1.85:5678/workflow/GDH4I878uz44yXDC
**Nodes:** 17

## Step-by-Step Flow

### Step 1: Multi-Channel Intake Webhook 🔌
**Type:** Trigger
**Description:** Receives classified intake data from any channel intake workflow

![Step 1](./intelligence_loop_step01.png)

### Step 2: Normalize Intake Data 🔄
**Type:** Transform
**Description:** Standardizes data format across all channels

![Step 2](./intelligence_loop_step02.png)

### Step 3: Extract Intent + Persona 🧠
**Type:** AI/ML
**Description:** Calls FastAPI /api/v1/intent for LLM-powered classification

![Step 3](./intelligence_loop_step03.png)

### Step 4: Capture Intent Output 🔄
**Type:** Transform
**Description:** Stores classified intent, persona, confidence, and SOP routing

![Step 4](./intelligence_loop_step04.png)

### Step 5: KB Search (ChromaDB) 🔍
**Type:** Retrieval
**Description:** Searches ChromaDB for relevant knowledge base articles

![Step 5](./intelligence_loop_step05.png)

### Step 6: Route by Result Type 🔀
**Type:** Router
**Description:** Switch: KB answer found → Draft Reply; Gap found → Flag Gap; Shopify → Lookup

![Step 6](./intelligence_loop_step06.png)

### Step 7: Draft BOLDR Reply 🧠
**Type:** AI/ML
**Description:** Generates channel-aware, persona-aware reply using GLM-5.1

![Step 7](./intelligence_loop_step07.png)

### Step 8: Queue for Human Approval 👤
**Type:** Human-in-Loop
**Description:** Writes draft to Google Sheets for human review before sending

![Step 8](./intelligence_loop_step08.png)

### Step 9: Flag Knowledge Gap 📝
**Type:** Feedback
**Description:** Logs unanswered questions to FastAPI /api/v1/kb/gap

![Step 9](./intelligence_loop_step09.png)

### Step 10: Shopify Product Lookup 🛒
**Type:** Integration
**Description:** Checks Shopify for product availability and pricing

![Step 10](./intelligence_loop_step10.png)

### Step 11: Shopify Answerable? 🔀
**Type:** Router
**Description:** IF node: Can we answer from Shopify data?

![Step 11](./intelligence_loop_step11.png)

### Step 12: Draft Shopify Reply 🧠
**Type:** AI/ML
**Description:** Generates product-specific reply with Shopify data

![Step 12](./intelligence_loop_step12.png)

### Step 13: Generate Human Handoff Reply 🧠
**Type:** AI/ML
**Description:** Creates polite handoff message for escalation cases

![Step 13](./intelligence_loop_step13.png)

### Step 14: Auto-Draft KB Entry 📈
**Type:** Self-Improve
**Description:** Auto-generates draft KB article from gap analysis (self-improvement)

![Step 14](./intelligence_loop_step14.png)

### Step 15: Weekly Theme Clustering ⏰
**Type:** Scheduled
**Description:** Scheduled trigger: clusters weekly themes from customer queries

![Step 15](./intelligence_loop_step15.png)

### Step 16: Monthly Marketing Brief ⏰
**Type:** Scheduled
**Description:** Scheduled trigger: generates marketing intelligence brief

![Step 16](./intelligence_loop_step16.png)

### Step 17: Send Webhook Response ✉️
**Type:** Response
**Description:** Returns final response to the originating channel

![Step 17](./intelligence_loop_step17.png)
