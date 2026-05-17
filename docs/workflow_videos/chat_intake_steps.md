# BOLDR Chat Intake Workflow

**Workflow ID:** `shrn8Mr1CIIAitjI`
**n8n URL:** http://192.168.1.85:5678/workflow/shrn8Mr1CIIAitjI
**Nodes:** 4

## Step-by-Step Flow

### Step 1: Chat Webhook 🔌
**Type:** Trigger
**Description:** Receives incoming chat messages via POST /webhook/chat

![Step 1](./chat_intake_step01.png)

### Step 2: Normalize Chat Data 🔄
**Type:** Transform
**Description:** Extracts channel, customer_id, message, metadata from payload

![Step 2](./chat_intake_step02.png)

### Step 3: Forward to Intelligence Loop ➡️
**Type:** Action
**Description:** Sends normalized data to FastAPI /api/v1/intake for classification

![Step 3](./chat_intake_step03.png)

### Step 4: Respond to Chat Widget ✉️
**Type:** Response
**Description:** Returns acknowledgment to the customer: 'Your message has been received'

![Step 4](./chat_intake_step04.png)
