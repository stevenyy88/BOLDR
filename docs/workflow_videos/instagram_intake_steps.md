# BOLDR Instagram DM Intake Workflow

**Workflow ID:** `LBAM9AM2t14lWrLv`
**n8n URL:** http://192.168.1.85:5678/workflow/LBAM9AM2t14lWrLv
**Nodes:** 4

## Step-by-Step Flow

### Step 1: Instagram DM Webhook 🔌
**Type:** Trigger
**Description:** Receives incoming Instagram DM messages via POST /webhook/instagram-dm

![Step 1](./instagram_intake_step01.png)

### Step 2: Normalize Instagram Data 🔄
**Type:** Transform
**Description:** Maps Instagram payload fields to BOLDR standard format

![Step 2](./instagram_intake_step02.png)

### Step 3: Forward to Intelligence Loop ➡️
**Type:** Action
**Description:** Sends normalized data to FastAPI /api/v1/intake for classification

![Step 3](./instagram_intake_step03.png)

### Step 4: Respond to Instagram ✉️
**Type:** Response
**Description:** Returns acknowledgment to the customer via Instagram DM

![Step 4](./instagram_intake_step04.png)
